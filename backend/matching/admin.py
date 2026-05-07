from django.contrib import admin
from .models import ResultatMatching

@admin.register(ResultatMatching)
class ResultatMatchingAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'offre', 'score_total', 'date_calcul']