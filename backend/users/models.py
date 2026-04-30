from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Champs supplémentaires par rapport au User Django de base
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True)
    localisation = models.CharField(max_length=100, blank=True)
    experience_annees = models.IntegerField(default=0)
    competences = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.username