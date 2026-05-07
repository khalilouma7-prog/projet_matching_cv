from typing import Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apps.matching.clustering import build_job_clusters
from apps.matching.geoutils import geocode_city
from apps.matching.jaccard import compute_jaccard_similarity
from apps.matching.scoring import (
    compute_experience_match,
    compute_geo_match,
    compute_weighted_score,
)
from apps.scraping.models import JobOffer


def compute_matching(
    user_text: str,
    user_experience_years: float = 0.0,
    user_city: str = "",
) -> Dict[str, object]:
    """
    Compute matching scores for all offers.
    Formula from project brief:
      score = 0.5*cosine + 0.25*jaccard + 0.15*exp + 0.10*geo
    Also applies K-Means clustering on offers.
    """
    jobs = list(JobOffer.objects.all())
    if not jobs:
        return {"results": [], "clustering": {"optimal_k": 0}}

    job_texts = [job.description or "" for job in jobs]
    documents = [user_text] + job_texts

    vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    cluster_labels, optimal_k = build_job_clusters(job_texts)

    results = []
    for i, job in enumerate(jobs):
        job_text = job.description or ""
        cosine_score = float(cosine_scores[i])
        jaccard_score = compute_jaccard_similarity(user_text, job_text)
        exp_score = compute_experience_match(
            user_exp_years=float(user_experience_years or 0.0),
           job_exp_text=job.experience or "",         )
        geo_score = compute_geo_match(user_city=user_city, job_location=job.location or "")
        lat, lng = geocode_city(job.location or "")

        final_score = compute_weighted_score(
            cosine_score=cosine_score,
            jaccard_score=jaccard_score,
            experience_score=exp_score,
            geo_score=geo_score,
        )

        results.append(
    {
        "job_id": job.id,
        "job": job.title,
        "company": job.company,
        "location": job.location,
        "contract": job.contract,  # ← AJOUTE CETTE LIGNE
        "lat": lat,
        "lng": lng,
        "cluster_id": int(cluster_labels[i]),
        "cosine_score": float(round(cosine_score * 100, 2)),
        "jaccard_score": float(round(jaccard_score * 100, 2)),
        "experience_score": float(round(exp_score * 100, 2)),
        "geo_score": float(round(geo_score * 100, 2)),
        "final_score": float(round(final_score * 100, 2)),
    }
)

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return {"results": results, "clustering": {"optimal_k": optimal_k}}