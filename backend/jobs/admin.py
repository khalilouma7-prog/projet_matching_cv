from django.contrib import admin
from .models import Offre

@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'entreprise', 'localisation', 'type_contrat', 'date_scraping']
    search_fields = ['titre', 'entreprise', 'localisation']
    list_filter = ['type_contrat']