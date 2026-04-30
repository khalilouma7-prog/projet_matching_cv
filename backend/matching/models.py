from django.db import models
from django.conf import settings
from jobs.models import Offre

class ResultatMatching(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    offre = models.ForeignKey(
        Offre, 
        on_delete=models.CASCADE
    )
    score_total = models.FloatField()
    score_cosinus = models.FloatField()
    score_jaccard = models.FloatField()
    score_experience = models.FloatField()
    score_geo = models.FloatField()
    date_calcul = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} → {self.offre} : {self.score_total}%"