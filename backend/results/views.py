from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from results.models import MatchResult 

@login_required
@require_http_methods(["GET"])
def get_results(request):
    results = MatchResult.objects.filter(user=request.user).select_related("job")
    data = [
        {
            "job_id": r.job.id,
            "job_title": r.job.title,
            "company": r.job.company,
            "location": r.job.location,
            "final_score": r.final_score,
            "created_at": r.created_at.isoformat(),
        }
        for r in results.order_by("-final_score")
    ]
    return JsonResponse({"success": True, "results": data})