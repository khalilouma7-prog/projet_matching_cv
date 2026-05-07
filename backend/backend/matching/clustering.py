from typing import List, Tuple

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


def build_job_clusters(job_texts: List[str]) -> Tuple[List[int], int]:
    """
    Cluster offers with K-Means and select best K using silhouette score.
    Returns tuple: (cluster_labels, optimal_k).
    """
    n_jobs = len(job_texts)
    if n_jobs < 2:
        return [0] * n_jobs, 1

    vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
    matrix = vectorizer.fit_transform(job_texts)

    max_k = min(8, n_jobs - 1)
    if max_k < 2:
        model = KMeans(n_clusters=1, random_state=42, n_init=10)
        return model.fit_predict(matrix).tolist(), 1

    best_k = 2
    best_score = -1.0
    best_labels = None

    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(matrix)
        score = silhouette_score(matrix, labels)
        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels

    return best_labels.tolist() if best_labels is not None else [0] * n_jobs, best_k
