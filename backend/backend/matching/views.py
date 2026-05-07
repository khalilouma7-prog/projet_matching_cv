from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.matching.geoutils import geocode_city
from apps.matching.matching_engine import compute_matching
from apps.nlp_engine.cv_reader import read_cv_file
from apps.nlp_engine.cleaner import clean_cv_text
from apps.auth_users.models import UploadedCV, UserProfile
from apps.scraping.models import JobOffer

@csrf_exempt
def match_uploaded_cv_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use POST method"}, status=405)

    if "cv" not in request.FILES:
        return JsonResponse({"error": "No CV file uploaded"}, status=400)

    cv_file = request.FILES["cv"]

    if not (cv_file.name.endswith(".pdf") or cv_file.name.endswith(".docx")):
        return JsonResponse({"error": "Only PDF and DOCX files are allowed"}, status=400)

    uploaded_cv = UploadedCV.objects.create(file=cv_file)
    file_path = uploaded_cv.file.path

    try:
        cv_text = read_cv_file(file_path)
        cleaned_cv = clean_cv_text(cv_text)

        user_profile = None
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.filter(user=request.user).first()

        matching_payload = compute_matching(
            cleaned_cv,
            user_experience_years=(user_profile.experience_years if user_profile else 0.0),
            user_city=(user_profile.city if user_profile else ""),
        )
        results = matching_payload["results"]

        return JsonResponse({
            "filename": cv_file.name,
            "total_results": len(results),
            "clustering": matching_payload["clustering"],
            "results": results[:10],
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def map_offers_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Use GET method"}, status=405)

    offers = JobOffer.objects.all()
    points = []
    for offer in offers:
        lat, lng = geocode_city(offer.location or "")
        if lat is None or lng is None:
            continue
        points.append(
            {
                "job_id": offer.id,
                "title": offer.title,
                "company": offer.company,
                "location": offer.location,
                "lat": lat,
                "lng": lng,
            }
        )

    return JsonResponse({"total": len(points), "points": points})
