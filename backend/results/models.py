from django.db import models
from django.contrib.auth.models import User
from apps.scraping.models import JobOffer

class MatchResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    final_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job.title} - {self.final_score}"