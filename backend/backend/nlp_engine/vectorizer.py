"""
vectorizer.py
TF-IDF vectorisation for CV texts and job offers.
Supports model persistence (save / load) via joblib.
"""
 
import os
import joblib
import numpy as np
from typing import List, Optional, Tuple
 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
 
from .preprocessor import preprocess_for_tfidf
 
# ──────────────────────────────────────────────
# Default paths
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models_saved")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")
MATRIX_PATH = os.path.join(MODEL_DIR, "tfidf_matrix.joblib")
 
os.makedirs(MODEL_DIR, exist_ok=True)
 
 
# ──────────────────────────────────────────────
# CVVectorizer class
# ──────────────────────────────────────────────
 
class CVVectorizer:
    """
    Wraps sklearn TfidfVectorizer with:
      - automatic text preprocessing
      - fit/transform/save/load helpers
    """
 
    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 1,
        sublinear_tf: bool = True,
    ):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            sublinear_tf=sublinear_tf,
            analyzer="word",
        )
        self.is_fitted = False
        self._matrix = None   # stored after fit_transform
 
    # ── Preprocessing ──────────────────────────
 
    def _preprocess(self, texts: List[str]) -> List[str]:
        """Run NLP preprocessing on each text."""
        return [preprocess_for_tfidf(t) for t in texts]
 
    # ── Fit / Transform ────────────────────────
 
    def fit(self, texts: List[str]) -> "CVVectorizer":
        """Fit the vectoriser on a corpus of texts."""
        cleaned = self._preprocess(texts)
        self.vectorizer.fit(cleaned)
        self.is_fitted = True
        return self
 
    def transform(self, texts: List[str]):
        """Transform texts into a TF-IDF sparse matrix."""
        if not self.is_fitted:
            raise RuntimeError("Vectorizer is not fitted yet. Call fit() first.")
        cleaned = self._preprocess(texts)
        return self.vectorizer.transform(cleaned)
 
    def fit_transform(self, texts: List[str]):
        """Fit and transform in one step."""
        cleaned = self._preprocess(texts)
        self._matrix = self.vectorizer.fit_transform(cleaned)
        self.is_fitted = True
        return self._matrix
 
    def transform_single(self, text: str):
        """Transform a single text (CV or offer description)."""
        return self.transform([text])
 
    # ── Similarity ─────────────────────────────
 
    def cosine_similarity_score(self, vec_a, vec_b) -> float:
        """Return cosine similarity (0-1) between two TF-IDF vectors."""
        score = cosine_similarity(vec_a, vec_b)
        return float(score[0][0])
 
    def get_top_features(self, vector, top_n: int = 20) -> List[Tuple[str, float]]:
        """Return the top N TF-IDF features for a given vector."""
        if not self.is_fitted:
            return []
        feature_names = self.vectorizer.get_feature_names_out()
        dense = np.array(vector.todense()).flatten()
        top_indices = dense.argsort()[::-1][:top_n]
        return [(feature_names[i], float(dense[i])) for i in top_indices if dense[i] > 0]
 
    # ── Persistence ────────────────────────────
 
    def save(
        self,
        vectorizer_path: str = VECTORIZER_PATH,
        matrix_path: Optional[str] = None,
    ) -> None:
        """Save the fitted vectoriser (and optionally the matrix)."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save an unfitted vectorizer.")
        joblib.dump(self.vectorizer, vectorizer_path)
        if matrix_path and self._matrix is not None:
            joblib.dump(self._matrix, matrix_path)
        print(f"[CVVectorizer] Saved to {vectorizer_path}")
 
    def load(self, vectorizer_path: str = VECTORIZER_PATH) -> "CVVectorizer":
        """Load a previously saved vectoriser."""
        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"No saved vectorizer found at {vectorizer_path}")
        self.vectorizer = joblib.load(vectorizer_path)
        self.is_fitted = True
        print(f"[CVVectorizer] Loaded from {vectorizer_path}")
        return self
 
    @classmethod
    def load_saved(cls, vectorizer_path: str = VECTORIZER_PATH) -> "CVVectorizer":
        """Class-method shortcut: create instance and load."""
        instance = cls()
        return instance.load(vectorizer_path)
 
 
# ──────────────────────────────────────────────
# Standalone helpers (no class needed)
# ──────────────────────────────────────────────
 
def vectorize_texts(texts: List[str], max_features: int = 5000):
    """
    Quick helper: fit + transform a list of texts.
    Returns (vectorizer_instance, tfidf_matrix).
    """
    vec = CVVectorizer(max_features=max_features)
    matrix = vec.fit_transform(texts)
    return vec, matrix
 
 
def compute_cosine_similarity(cv_text: str, offer_text: str) -> float:
    """
    Compute cosine similarity between a CV and a job offer description.
    Fits a fresh vectorizer on both documents.
    """
    vec, matrix = vectorize_texts([cv_text, offer_text])
    cv_vec = matrix[0]
    offer_vec = matrix[1]
    return vec.cosine_similarity_score(cv_vec, offer_vec)
 
 
def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Jaccard similarity between two skill sets.
    J(A,B) = |A ∩ B| / |A ∪ B|
    """
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0
 