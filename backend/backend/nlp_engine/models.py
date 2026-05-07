from django.db import models
from django.contrib.auth.models import User
 
 
class CVDocument(models.Model):
    """Stores the uploaded CV file and its raw extracted text."""
 
    FILE_TYPE_CHOICES = [("pdf", "PDF"), ("docx", "DOCX"), ("other", "Other")]
 
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cv_documents"
    )
    file = models.FileField(upload_to="cvs/")
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default="pdf")
    raw_text = models.TextField(blank=True, default="")
    cleaned_text = models.TextField(blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
 
    class Meta:
        ordering = ["-uploaded_at"]
 
    def __str__(self):
        return f"CV of {self.user.username} ({self.file_type}) - {self.uploaded_at:%Y-%m-%d}"
 
 
class CVProfile(models.Model):
    """
    Structured profile extracted from a CVDocument.
    One profile per CV document.
    """
 
    cv_document = models.OneToOneField(
        CVDocument, on_delete=models.CASCADE, related_name="profile"
    )
 
    # ── Contact info ────────────────────────────
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
 
    # ── Extracted sections (raw text per section) ──
    summary_section = models.TextField(blank=True, default="")
    skills_section = models.TextField(blank=True, default="")
    experience_section = models.TextField(blank=True, default="")
    education_section = models.TextField(blank=True, default="")
    languages_section = models.TextField(blank=True, default="")
    projects_section = models.TextField(blank=True, default="")
    certifications_section = models.TextField(blank=True, default="")
    interests_section = models.TextField(blank=True, default="")
 
    # ── Detected skills (comma-separated flat list) ──
    detected_skills = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated list of detected technical skills",
    )
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"Profile for {self.cv_document}"
 
    def get_skills_list(self) -> list:
        """Return detected_skills as a Python list."""
        if not self.detected_skills:
            return []
        return [s.strip() for s in self.detected_skills.split(",") if s.strip()]
 
    def set_skills_list(self, skills: list) -> None:
        """Set detected_skills from a Python list."""
        self.detected_skills = ", ".join(skills)
 
 
class SkillVector(models.Model):
    """
    Stores the TF-IDF vector for a CV profile as a JSON-serialised
    list of (feature, score) tuples (top features only for storage).
    """
 
    cv_profile = models.OneToOneField(
        CVProfile, on_delete=models.CASCADE, related_name="skill_vector"
    )
 
    # Top TF-IDF features stored as JSON: [{"term": "python", "score": 0.45}, ...]
    tfidf_features = models.JSONField(default=list)
 
    # Preprocessed text used to build the vector (for re-vectorisation)
    preprocessed_text = models.TextField(blank=True, default="")
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"SkillVector for {self.cv_profile}"
 
    def get_feature_dict(self) -> dict:
        """Return tfidf_features as {term: score} dict."""
        return {item["term"]: item["score"] for item in self.tfidf_features}
 
    def get_skills_set(self) -> set:
        """Return set of all terms (for Jaccard similarity)."""
        return {item["term"] for item in self.tfidf_features}
 