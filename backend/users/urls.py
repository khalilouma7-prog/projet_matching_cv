from django.urls import path

from .views import api_root_view, login_view, register_view, user_profile_view

urlpatterns = [
    path("", api_root_view, name="api_root"),
    path("auth/register/", register_view, name="auth_register"),
    path("auth/login/", login_view, name="auth_login"),
    path("users/<int:user_id>/", user_profile_view, name="user_profile"),
]