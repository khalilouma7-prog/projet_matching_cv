import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.auth_users.models import UserProfile


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"success": False, "error": message}, status=status)


def _json_ok(data: dict, status: int = 200) -> JsonResponse:
    return JsonResponse({"success": True, **data}, status=status)


@require_http_methods(["GET"])
def api_root_view(request):
    return _json_ok(
        {
            "message": "CV Matching API is running.",
            "endpoints": {
                "auth_register": "/api/auth/register/",
                "auth_login": "/api/auth/login/",
                "user_profile_get_put": "/api/users/<user_id>/",
                "match_cv": "/api/match-cv/",
                "map_offers": "/api/map-offers/",
                "nlp": "/api/nlp/",
            },
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    full_name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not full_name or not email or not password:
        return _json_error("name, email and password are required.")
    if User.objects.filter(username=email).exists():
        return _json_error("Email already exists.", status=409)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=full_name,
    )
    profile = UserProfile.objects.create(user=user, full_name=full_name)

    return _json_ok(
        {
            "user": {
                "id": user.id,
                "name": profile.full_name,
                "email": user.email,
                "city": profile.city,
                "experience_years": profile.experience_years,
                "skills_manual": profile.skills_manual or "",
                "education": profile.education or "",
            }
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or not password:
        return _json_error("email and password are required.")

    user = authenticate(request, username=email, password=password)
    if not user:
        return _json_error("Invalid credentials.", status=401)

    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"full_name": user.first_name or email})
    return _json_ok(
        {
            "user": {
                "id": user.id,
                "name": profile.full_name,
                "email": user.email,
                "city": profile.city,
                "experience_years": profile.experience_years,
                "skills_manual": profile.skills_manual or "",
                "education": profile.education or "",
            }
        }
    )


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def user_profile_view(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return _json_error("User not found.", status=404)

    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"full_name": user.first_name or user.username})

    if request.method == "GET":
        return _json_ok(
            {
                "profile": {
                    "id": user.id,
                    "name": profile.full_name,
                    "email": user.email,
                    "city": profile.city or "",
                    "experience_years": profile.experience_years or 0,
                    "skills_manual": profile.skills_manual or "",
                    "education": profile.education or "",
                }
            }
        )

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error("Invalid JSON.")

    profile.full_name = body.get("name", profile.full_name)
    profile.city = body.get("city", profile.city)
    profile.experience_years = float(body.get("experience_years", profile.experience_years or 0))
    profile.skills_manual = body.get("skills_manual", profile.skills_manual)
    profile.education = body.get("education", profile.education)
    profile.save()

    user.first_name = profile.full_name
    user.email = body.get("email", user.email)
    user.username = user.email
    user.save()

    return _json_ok(
        {
            "profile": {
                "id": user.id,
                "name": profile.full_name,
                "email": user.email,
                "city": profile.city or "",
                "experience_years": profile.experience_years or 0,
                "skills_manual": profile.skills_manual or "",
                "education": profile.education or "",
            }
        }
    )