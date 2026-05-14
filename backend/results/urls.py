from django.urls import path
from .views import get_results

urlpatterns = [
    path("", get_results, name="get_results"),
]