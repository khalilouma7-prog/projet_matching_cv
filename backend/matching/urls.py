from django.urls import path
from . import views

urlpatterns = [
    path('lancer/', views.lancer_matching, name='matching'),
]