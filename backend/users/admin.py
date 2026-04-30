from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'localisation', 'experience_annees']
    fieldsets = UserAdmin.fieldsets + (
        ('Infos supplémentaires', {
            'fields': ('cv_file', 'localisation', 'experience_annees', 'competences')
        }),
    )