from django.urls import path
from . import views

urlpatterns = [
    path("upload-cv/", views.upload_cv, name="nlp_upload_cv"),
    path("profile/<int:profile_id>/", views.get_profile, name="nlp_get_profile"),
    path("vectorize/", views.vectorize_text, name="nlp_vectorize"),
    path("extract-skills/", views.extract_skills, name="nlp_extract_skills"),
]