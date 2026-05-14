from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from apps.matching.matching_engine import compute_matching
from apps.matching.geoutils import geocode_city
from apps.matching.scoring import (
    compute_experience_match,
    compute_geo_match,
    compute_weighted_score,
)
from apps.scraping.models import JobOffer


class MatchingEngineTests(TestCase):
    def setUp(self):
        JobOffer.objects.create(
            title="Data Scientist",
            company="A",
            location="Casablanca",
            experience_required="2 years",
            description="python machine learning pandas numpy nlp",
        )
        JobOffer.objects.create(
            title="Backend Engineer",
            company="B",
            location="Rabat",
            experience_required="4 years",
            description="django python rest api postgresql",
        )
        JobOffer.objects.create(
            title="Frontend Developer",
            company="C",
            location="Marrakech",
            experience_required="1 year",
            description="react javascript html css frontend ui",
        )

    def test_weighted_formula_is_applied(self):
        score = compute_weighted_score(
            cosine_score=0.8,
            jaccard_score=0.6,
            experience_score=1.0,
            geo_score=0.5,
        )
        self.assertAlmostEqual(score, 0.75, places=6)

    def test_sub_scores_helpers(self):
        self.assertEqual(compute_experience_match(3, "2 years"), 1.0)
        self.assertGreater(compute_experience_match(1, "4 years"), 0.0)
        self.assertEqual(compute_geo_match("Casablanca", "Casablanca"), 1.0)
        self.assertEqual(compute_geo_match("", "Casablanca"), 0.5)

    def test_compute_matching_returns_sorted_results_and_clustering(self):
        payload = compute_matching(
            user_text="python machine learning django rest api",
            user_experience_years=3,
            user_city="Casablanca",
        )

        self.assertIn("results", payload)
        self.assertIn("clustering", payload)
        self.assertIn("optimal_k", payload["clustering"])
        self.assertGreaterEqual(payload["clustering"]["optimal_k"], 1)

        results = payload["results"]
        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(results[0]["final_score"], results[-1]["final_score"])
        self.assertIn("cluster_id", results[0])
        self.assertIn("lat", results[0])
        self.assertIn("lng", results[0])


class MatchingApiTests(TestCase):
    def setUp(self):
        JobOffer.objects.create(
            title="Data Analyst",
            company="D",
            location="Casablanca",
            experience_required="1 year",
            description="python pandas sql reporting data visualization",
        )

    @patch("apps.matching.views.clean_cv_text")
    @patch("apps.matching.views.read_cv_file")
    def test_match_cv_api_returns_payload(self, mock_read_cv_file, mock_clean_cv_text):
        mock_read_cv_file.return_value = "Python SQL pandas machine learning"
        mock_clean_cv_text.return_value = "python sql pandas machine learning"

        cv_file = SimpleUploadedFile(
            "sample_cv.pdf",
            b"%PDF-1.4 test content",
            content_type="application/pdf",
        )

        response = self.client.post("/api/match-cv/", {"cv": cv_file})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("filename", body)
        self.assertIn("total_results", body)
        self.assertIn("clustering", body)
        self.assertIn("results", body)
        self.assertGreaterEqual(body["total_results"], 1)

    def test_map_offers_api_returns_geo_points(self):
        response = self.client.get("/api/map-offers/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("points", payload)
        self.assertGreaterEqual(payload["total"], 1)
        self.assertIn("lat", payload["points"][0])
        self.assertIn("lng", payload["points"][0])

    def test_geocode_city_known_value(self):
        lat, lng = geocode_city("Casablanca")
        self.assertIsNotNone(lat)
        self.assertIsNotNone(lng)
