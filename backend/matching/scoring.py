import re


def extract_years(text: str) -> float:
    """Extract first numeric experience hint from free text."""
    if not text:
        return 0.0

    match = re.search(r"(\d+(?:[.,]\d+)?)", text.lower())
    if not match:
        return 0.0
    return float(match.group(1).replace(",", "."))


def compute_experience_match(user_exp_years: float, job_exp_text: str) -> float:
    """
    Experience score in [0, 1].
    - 1.0 when user meets/exceeds requirement
    - 0.5 when requirement missing
    """
    required = extract_years(job_exp_text)
    if required <= 0:
        return 0.5
    if user_exp_years <= 0:
        return 0.0
    if user_exp_years >= required:
        return 1.0
    return max(0.0, user_exp_years / required)


def compute_geo_match(user_city: str, job_location: str) -> float:
    """Simple city overlap score in [0, 1]."""
    if not user_city or not job_location:
        return 0.5

    user_city_l = user_city.strip().lower()
    job_location_l = job_location.strip().lower()

    if user_city_l == job_location_l:
        return 1.0
    if user_city_l in job_location_l or job_location_l in user_city_l:
        return 0.8
    return 0.0


def compute_weighted_score(
    cosine_score: float,
    jaccard_score: float,
    experience_score: float,
    geo_score: float,
) -> float:
    """Weighted score from project brief in [0, 1]."""
    return (
        (0.5 * cosine_score)
        + (0.25 * jaccard_score)
        + (0.15 * experience_score)
        + (0.10 * geo_score)
    )