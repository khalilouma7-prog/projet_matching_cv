from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg
from collections import Counter
from results.models import MatchResult
from scraping.models import JobOffer

# ==========================================
# 1. VUE POUR LA PAGE "MES RÉSULTATS"
# ==========================================
@csrf_exempt
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

# ==========================================
# 2. VUE POUR LA PAGE "DASHBOARD GLOBAL"
# ==========================================
@csrf_exempt  # ✅ remplace @api_view + @permission_classes
@require_http_methods(["GET"])
def dashboard_global_stats(request):
    CLUSTER_NAMES = {
        0: "Informatique & IT",
        1: "Finance & Comptabilité",
        2: "Marketing & Ventes",
        3: "Ressources Humaines",
        4: "Ingénierie & Industrie",
        5: "Administration",
        6: "Support Client",
        7: "Logistique"
    }
    CLUSTER_COLORS = ["#3d7fff","#a855f7","#f59e0b","#ef4444","#00e5a0","#06b6d4","#f43f5e","#8b5cf6"]

    # KPIs
    total_offres = JobOffer.objects.count()
    domaines_count = JobOffer.objects.filter(cluster_id__isnull=False).values('cluster_id').distinct().count()

    # Stats utilisateur si connecté
    cv_analyses = 0
    avg_score = 0
    history_data = []
    if request.user.is_authenticated:
        cv_analyses = MatchResult.objects.filter(user=request.user).dates('created_at', 'day').count()
        avg_dict = MatchResult.objects.filter(user=request.user).aggregate(Avg('final_score'))
        avg_score = round(avg_dict['final_score__avg'] or 0)
        recent = MatchResult.objects.filter(user=request.user).select_related('job').order_by('-created_at')[:3]
        for match in recent:
            history_data.append({
                "id": match.id,
                "date": match.created_at.strftime("%d %b %Y"),
                "cv": "Profil CV",
                "topMatch": f"{round(match.final_score, 1)}%",
                "domaine": CLUSTER_NAMES.get(match.job.cluster_id, "Non précisé")
            })

    # Clusters
    clusters_db = JobOffer.objects.filter(cluster_id__isnull=False).values('cluster_id').annotate(count=Count('id')).order_by('-count')[:5]
    clusters_data = []
    for i, item in enumerate(clusters_db):
        c_id = item['cluster_id']
        clusters_data.append({
            "label": CLUSTER_NAMES.get(c_id, f"Cluster {c_id}"),
            "count": item['count'],
            "color": CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        })

    # Top Skills
    all_skills = []
    for offer in JobOffer.objects.exclude(skills=[]).order_by('-scraped_at')[:500]:
        if isinstance(offer.skills, list):
            all_skills.extend(offer.skills)
    word_counts = Counter(all_skills).most_common(12)
    global_words = [
        {
            "text": w.capitalize(),
            "size": min(45, max(16, c)),
            "color": CLUSTER_COLORS[i % len(CLUSTER_COLORS)],
            "opacity": 0.9
        }
        for i, (w, c) in enumerate(word_counts)
    ]

    return JsonResponse({
        "kpis": {
            "total_offres": total_offres,
            "domaines_count": domaines_count,
            "cv_analyses": cv_analyses,
            "avg_score": avg_score
        },
        "clustersGlobal": clusters_data,
        "globalWords": global_words,
        "historyData": history_data
    })