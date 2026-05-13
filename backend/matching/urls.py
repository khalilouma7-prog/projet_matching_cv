from django.urls import path
from .views import match_uploaded_cv_view, map_offers_view

urlpatterns = [
    path("match-cv/", match_uploaded_cv_view, name="match_cv"),
    path("map-offers/", map_offers_view, name="map_offers"),
]