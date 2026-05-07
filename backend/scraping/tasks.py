# backend/scraping/tasks.py
import subprocess
import json
import tempfile
import os
from celery import shared_task
from django.utils import timezone

from .models import JobOffer, ScrapingSource


@shared_task(name="apps.scraping.tasks.scrape_all_sources")
def scrape_all_sources():
    """Lance le scraping sur toutes les sources actives."""
    sources = ScrapingSource.objects.filter(is_active=True)
    for source in sources:
        scrape_source.delay(source.name)


@shared_task(name="apps.scraping.tasks.scrape_source")
def scrape_source(source_name: str):
    """
    Lance le spider Scrapy correspondant à la source,
    puis sauvegarde les offres en base de données.
    """
    spider_map = {
        "rekrute":  "rekrute",
        "emploima": "emploima",
        "indeed":   "indeed",
    }

    spider = spider_map.get(source_name)
    if not spider:
        return {"error": f"Source inconnue : {source_name}"}

    # Fichier temporaire pour récupérer les résultats Scrapy
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_path = tmp.name

    try:
        # Lancer le spider via subprocess
        result = subprocess.run(
            ["scrapy", "crawl", spider, "-o", output_path, "-t", "json"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True, text=True, timeout=300,
        )

        with open(output_path, "r", encoding="utf-8") as f:
            offers_data = json.load(f)

        saved = save_offers(offers_data, source_name)

        # Mettre à jour le statut de la source
        ScrapingSource.objects.filter(name=source_name).update(
            last_run=timezone.now(),
            nb_offers=JobOffer.objects.filter(source=source_name).count(),
        )
        return {"source": source_name, "saved": saved}

    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def save_offers(offers_data: list, source: str) -> int:
    """Sauvegarde les offres scrappées en base de données."""
    from apps.nlp_engine.preprocessor import preprocess_text
    from apps.nlp_engine.vectorizer   import build_tfidf_vector

    saved = 0
    for item in offers_data:
        url = item.get("url", "").strip()
        if not url:
            continue

        # Construire le texte complet pour le vecteur TF-IDF
        full_text = f"{item.get('title','')} {item.get('description','')} {' '.join(item.get('skills',[]))}"
        tokens    = preprocess_text(full_text)

        offer, created = JobOffer.objects.update_or_create(
            url=url,
            defaults={
                "title":       item.get("title", "")[:255],
                "company":     item.get("company", "")[:255],
                "sector":      item.get("sector",  "")[:100],
                "location":    item.get("location","")[:150],
                "contract":    item.get("contract","Autre")[:20],
                "experience":  item.get("experience","")[:50],
                "description": item.get("description",""),
                "skills":      item.get("skills", []),
                "source":      source,
                "published_at":item.get("published_at"),
            },
        )
        if created:
            saved += 1

    return saved
