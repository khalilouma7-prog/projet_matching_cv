from django.shortcuts import render

# Create your views here.
# backend/apps/scraping/views.py
from rest_framework.views     import APIView
from rest_framework.response  import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import JobOffer, ScrapingSource
from .tasks  import scrape_source


class ScrapingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sources = ScrapingSource.objects.all()
        data = [
            {
                "id":        s.name,
                "name":      s.name,
                "active":    s.is_active,
                "count":     s.nb_offers,
                "last_run":  s.last_run,
            }
            for s in sources
        ]
        return Response(data)


class ScrapingTriggerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        source = request.data.get("source")
        if not source:
            return Response({"error": "Source requise."}, status=400)
        scrape_source.delay(source)
        return Response({"detail": f"Scraping lancé pour : {source}"})


class ScrapingSourceToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, source_id):
        active = request.data.get("active")
        ScrapingSource.objects.filter(name=source_id).update(is_active=active)
        return Response({"detail": "Mis à jour."})
