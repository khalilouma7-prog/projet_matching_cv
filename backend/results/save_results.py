from django.contrib.auth.models import User
from results.models import MatchResult          # ✅ corrigé
from scraping.models import JobOffer            # ✅ corrigé
from matching.matching_engine import compute_matching  # ✅ corrigé

def save_matching_results(username, user_text):
    user = User.objects.get(username=username)
    MatchResult.objects.filter(user=user).delete()

    payload = compute_matching(user_text)
    results = payload["results"]

    for item in results:
        job = JobOffer.objects.get(id=item["job_id"])
        MatchResult.objects.create(
            user=user,
            job=job,
            final_score=item["final_score"]
        )
    print("Matching results saved successfully!")