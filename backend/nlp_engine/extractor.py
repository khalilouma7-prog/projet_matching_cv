import re
 
 
# ──────────────────────────────────────────────
# Section keywords map  (FR + EN)
# ──────────────────────────────────────────────
SECTION_KEYWORDS = {
    "skills": [
        "compétences", "competences", "skills", "technical skills",
        "compétences techniques", "outils", "technologies",
    ],
    "education": [
        "formation", "éducation", "education", "diplômes", "diplomes",
        "études", "etudes", "parcours académique", "scolarité",
    ],
    "experience": [
        "expériences professionnelles", "experiences professionnelles",
        "expérience professionnelle", "experience professionnelle",
        "expérience", "experience", "parcours professionnel",
        "emplois", "postes occupés", "work experience",
    ],
    "languages": [
        "langues", "languages", "langue parlée", "langue parlée",
    ],
    "interests": [
        "centres d'intérêt", "centres d'interet", "centres d interet",
        "loisirs", "hobbies", "interests", "activités",
    ],
    "summary": [
        "profil", "résumé", "resume", "à propos", "about", "objectif",
        "présentation", "presentation",
    ],
    "certifications": [
        "certifications", "certificats", "certificates", "accréditations",
    ],
    "projects": [
        "projets", "projects", "réalisations", "portfolio",
    ],
}
 
# Order matters: sections are detected in this priority
SECTION_ORDER = [
    "summary", "experience", "education", "skills",
    "languages", "certifications", "projects", "interests",
]
 
 
def extract_text_sections(text: str) -> dict:
    """
    Split a raw CV text into named sections.
    Returns a dict  {section_name: raw_text_of_section}.
    Sections not found will have an empty string value.
    """
    sections = {s: "" for s in SECTION_ORDER}
    lower = text.lower()
    lines = text.splitlines()
 
    # Build a list of (line_index, section_name) for each detected heading
    detected = []
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if not line_lower:
            continue
        for section_name, keywords in SECTION_KEYWORDS.items():
            if any(kw in line_lower for kw in keywords):
                detected.append((i, section_name))
                break  # one section per line
 
    # Remove duplicate detections (keep first occurrence per section)
    seen = set()
    unique_detected = []
    for idx, sec in detected:
        if sec not in seen:
            seen.add(sec)
            unique_detected.append((idx, sec))
 
    # Slice text between consecutive headings
    for pos, (line_idx, sec_name) in enumerate(unique_detected):
        start_line = line_idx + 1  # skip the heading itself
        if pos + 1 < len(unique_detected):
            end_line = unique_detected[pos + 1][0]
        else:
            end_line = len(lines)
        sections[sec_name] = "\n".join(lines[start_line:end_line]).strip()
 
    return sections
 
 
def extract_contact_info(text: str) -> dict:
    """
    Extract basic contact info: email, phone, LinkedIn URL.
    """
    contact = {"email": None, "phone": None, "linkedin": None}
 
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"(\+?\d[\d\s\-().]{7,15}\d)"
    linkedin_pattern = r"(linkedin\.com/in/[^\s,)\"']+)"
 
    email_match = re.search(email_pattern, text)
    if email_match:
        contact["email"] = email_match.group()
 
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact["phone"] = phone_match.group().strip()
 
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group()
 
    return contact
 
 
def extract_all(text: str) -> dict:
    """
    Master extractor: returns sections + contact info.
    """
    return {
        "sections": extract_text_sections(text),
        "contact":  extract_contact_info(text),
    }
 