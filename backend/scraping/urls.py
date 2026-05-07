
from django.urls import path
from .views import ScrapingStatusView, ScrapingTriggerView, ScrapingSourceToggleView

urlpatterns = [
    path("status/",             ScrapingStatusView.as_view(),           name="scraping-status"),
    path("trigger/",            ScrapingTriggerView.as_view(),          name="scraping-trigger"),
    path("sources/<str:source_id>/", ScrapingSourceToggleView.as_view(), name="scraping-toggle"),
]