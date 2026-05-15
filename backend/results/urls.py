from django.urls import path
from .views import get_results
from . import views

urlpatterns = [
    path("", get_results, name="get_results"),
        path('dashboard-stats/', views.dashboard_global_stats, name='dashboard-stats'),

]
