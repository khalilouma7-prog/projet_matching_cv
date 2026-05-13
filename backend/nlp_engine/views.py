from django.shortcuts import render

"""
views.py
Django REST API views for the NLP engine.

Endpoints:
  POST /nlp/upload-cv/          → Upload + process a CV
  GET  /nlp/profile/<id>/       → Get extracted profile
  POST /nlp/vectorize/          → Vectorise CV text
  POST /nlp/extract-skills/     → Extract skills from raw text
"""

import json
import tempfile
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import CVDocument, CVProfile, SkillVector
from .cv_reader import read_cv_file
from .cleaner import clean_cv_text
from .extractor import extract_all
from .preprocessor import extract_skills_flat, preprocess_for_tfidf
from .vectorizer import CVVectorizer


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"success": False, "error": message}, status=status)


def _json_ok(data: dict, status: int = 200) -> JsonResponse:
    return JsonResponse({"success": True, **data}, status=status)


# ──────────────────────────────────────────────
# View: Upload & Process CV
# ──────────────────────────────────────────────

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def upload_cv(request):
    """
    Upload a CV file (PDF or DOCX), extract text, detect skills,
    store everything in the database.
    """
    if "file" not in request.FILES:
        return _json_error("No file provided.")

    uploaded_file = request.FILES["file"]
    filename = uploaded_file.name.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        return _json_error("Only PDF and DOCX files are supported.")

    file_type = "pdf" if filename.endswith(".pdf") else "docx"

    # Save uploaded file to a temp location to read it
    suffix = "." + file_type
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        # ── 1. Read raw text ──
        raw_text = read_cv_file(tmp_path)
        if not raw_text.strip():
            return _json_error("Could not extract text from the file.")

        # ── 2. Clean ──
        cleaned_text = clean_cv_text(raw_text)

        # ── 3. Extract sections + contact ──
        extraction = extract_all(cleaned_text)
        sections = extraction["sections"]
        contact = extraction["contact"]

        # ── 4. Detect skills ──
        skills = extract_skills_flat(cleaned_text)

        # ── 5. Vectorise ──
        preprocessed = preprocess_for_tfidf(cleaned_text)
        vec = CVVectorizer(max_features=3000)
        tfidf_matrix = vec.fit_transform([cleaned_text])
        top_features = vec.get_top_features(tfidf_matrix[0], top_n=50)
        tfidf_features_json = [
            {"term": term, "score": round(score, 4)}
            for term, score in top_features
        ]

        # ── 6. Save to DB ──
        cv_doc = CVDocument.objects.create(
            user=request.user,
            file=uploaded_file,
            file_type=file_type,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            processed=True,
        )

        profile = CVProfile.objects.create(
            cv_document=cv_doc,
            email=contact.get("email"),
            phone=contact.get("phone"),
            linkedin_url=contact.get("linkedin"),
            summary_section=sections.get("summary", ""),
            skills_section=sections.get("skills", ""),
            experience_section=sections.get("experience", ""),
            education_section=sections.get("education", ""),
            languages_section=sections.get("languages", ""),
            projects_section=sections.get("projects", ""),
            certifications_section=sections.get("certifications", ""),
            interests_section=sections.get("interests", ""),
        )
        profile.set_skills_list(skills)
        profile.save()

        SkillVector.objects.create(
            cv_profile=profile,
            tfidf_features=tfidf_features_json,
            preprocessed_text=preprocessed,
        )

    finally:
        os.unlink(tmp_path)

    return _json_ok({
        "cv_id": cv_doc.id,
        "profile_id": profile.id,
        "detected_skills": skills,
        "contact": contact,
        "sections_found": [k for k, v in sections.items() if v],
    }, status=201)


# ──────────────────────────────────────────────
# View: Get Profile
# ──────────────────────────────────────────────

@login_required
@require_http_methods(["GET"])
def get_profile(request, profile_id: int):
    """Return full extracted profile data for a given profile ID."""
    profile = get_object_or_404(CVProfile, id=profile_id, cv_document__user=request.user)

    skill_vector = getattr(profile, "skill_vector", None)

    data = {
        "profile_id": profile.id,
        "cv_id": profile.cv_document.id,
        "contact": {
            "email": profile.email,
            "phone": profile.phone,
            "linkedin": profile.linkedin_url,
        },
        "sections": {
            "summary": profile.summary_section,
            "skills": profile.skills_section,
            "experience": profile.experience_section,
            "education": profile.education_section,
            "languages": profile.languages_section,
            "projects": profile.projects_section,
            "certifications": profile.certifications_section,
            "interests": profile.interests_section,
        },
        "detected_skills": profile.get_skills_list(),
        "tfidf_top_features": skill_vector.tfidf_features if skill_vector else [],
        "created_at": profile.created_at.isoformat(),
    }
    return _json_ok(data)


# ──────────────────────────────────────────────
# View: Vectorise raw text (utility endpoint)
# ──────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def vectorize_text(request):
    """
    POST {"text": "..."} → returns top TF-IDF features.
    Useful for vectorising job offer descriptions on the fly.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error("Invalid JSON body.")

    text = body.get("text", "").strip()
    if not text:
        return _json_error("'text' field is required.")

    top_n = int(body.get("top_n", 30))

    vec = CVVectorizer(max_features=3000)
    matrix = vec.fit_transform([text])
    top_features = vec.get_top_features(matrix[0], top_n=top_n)

    return _json_ok({
        "top_features": [
            {"term": t, "score": round(s, 4)} for t, s in top_features
        ],
        "preprocessed_text": preprocess_for_tfidf(text),
    })


# ──────────────────────────────────────────────
# View: Extract skills from text (utility endpoint)
# ──────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def extract_skills(request):
    """
    POST {"text": "..."} → returns list of detected skills.
    Works for both CV text and job offer descriptions.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error("Invalid JSON body.")

    text = body.get("text", "").strip()
    if not text:
        return _json_error("'text' field is required.")

    from .preprocessor import extract_skills_from_text
    skills_by_category = extract_skills_from_text(text)
    skills_flat = extract_skills_flat(text)

    return _json_ok({
        "skills_flat": skills_flat,
        "skills_by_category": skills_by_category,
    })