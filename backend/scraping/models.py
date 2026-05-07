# backend/scraping/models.py
from django.db import models


class JobOffer(models.Model):
    CONTRACT_CHOICES = [
        ("CDI",       "CDI"),
        ("CDD",       "CDD"),
        ("Stage",     "Stage"),
        ("Freelance", "Freelance"),
        ("Autre",     "Autre"),
    ]

    # Données scrappées
    title       = models.CharField(max_length=255)
    company     = models.CharField(max_length=255)
    sector      = models.CharField(max_length=100, blank=True)
    location    = models.CharField(max_length=150, blank=True)
    contract    = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default="Autre")
    experience  = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    skills      = models.JSONField(default=list)   # ["Python", "SQL", ...]
    url         = models.URLField(max_length=500, unique=True)
    source      = models.CharField(max_length=50)  # "rekrute", "indeed"…
    published_at= models.DateField(null=True, blank=True)
    scraped_at  = models.DateTimeField(auto_now_add=True)

    # Vecteur TF-IDF (stocké après vectorisation)
    tfidf_vector = models.JSONField(default=dict, blank=True)

    # Cluster K-Means
    cluster_id   = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "job_offers"
        ordering = ["-scraped_at"]

    def __str__(self):
        return f"{self.title} — {self.company}"


class ScrapingSource(models.Model):
    """Configuration et état de chaque source de scraping."""
    name       = models.CharField(max_length=50, unique=True)
    url        = models.URLField()
    is_active  = models.BooleanField(default=True)
    last_run   = models.DateTimeField(null=True, blank=True)
    nb_offers  = models.IntegerField(default=0)

    class Meta:
        db_table = "scraping_sources"

    def __str__(self):
        return self.name
