from django.db import models

class Offre(models.Model):
    titre = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255, blank=True)
    localisation = models.CharField(max_length=100, blank=True)
    competences_requises = models.JSONField(default=list)
    experience_requise = models.IntegerField(default=0)
    type_contrat = models.CharField(max_length=50, blank=True)  # CDI, CDD, Stage...
    description = models.TextField(blank=True)
    url_source = models.URLField(max_length=500)
    date_publication = models.DateField(null=True, blank=True)
    date_scraping = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} - {self.entreprise}"