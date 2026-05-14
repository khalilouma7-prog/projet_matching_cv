import json

from django.test import TestCase


class AuthUsersApiTests(TestCase):
    def test_register_login_and_profile_update_flow(self):
        register_response = self.client.post(
            "/api/auth/register/",
            data=json.dumps(
                {
                    "name": "Test User",
                    "email": "testuser@example.com",
                    "password": "StrongPass123!",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(register_response.status_code, 201)
        user_id = register_response.json()["user"]["id"]

        login_response = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"email": "testuser@example.com", "password": "StrongPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json()["user"]["id"], user_id)

        update_response = self.client.put(
            f"/api/users/{user_id}/",
            data=json.dumps(
                {
                    "name": "Updated User",
                    "city": "Casablanca",
                    "experience_years": 2,
                    "skills_manual": "python, sql",
                    "education": "IASD",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["profile"]["city"], "Casablanca")
from django.test import TestCase

# Create your tests here.
