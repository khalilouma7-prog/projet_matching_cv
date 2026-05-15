"""
preprocessor.py
NLP pipeline : tokenisation → stop words removal → lemmatisation (spaCy)
+ technical skills dictionary for keyword extraction.
"""
 
import re
import spacy
from typing import List, Dict
 

# Load spaCy model (French + English fallback)

try:
    nlp = spacy.load("fr_core_news_md")
except OSError:
    try:
        nlp = spacy.load("fr_core_news_sm")
    except OSError:
        try:
            # Fallback to English model if available
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Last-resort fallback keeps API functional without external model downloads.
            nlp = spacy.blank("fr")
 
 

# Technical Skills Dictionary

TECHNICAL_SKILLS: Dict[str, List[str]] = {
    # Programming languages
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "ruby", "php", "swift", "kotlin", "go", "rust", "scala", "r",
        "matlab", "perl", "bash", "shell",
    ],
    # Web / Frontend
    "web_frontend": [
        "html", "css", "react", "vue", "angular", "next.js", "nuxt",
        "bootstrap", "tailwind", "sass", "scss", "webpack", "vite",
        "redux", "jquery",
    ],
    # Backend / Frameworks
    "web_backend": [
        "django", "flask", "fastapi", "spring", "node.js", "express",
        "laravel", "symfony", "rails", "asp.net",
    ],
    # Data / ML / AI
    "data_ml": [
        "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow",
        "pytorch", "keras", "xgboost", "lightgbm", "spacy", "nltk",
        "opencv", "matplotlib", "seaborn", "plotly",
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "data mining", "text mining", "tfidf", "tf-idf",
        "clustering", "k-means", "regression", "classification",
    ],
    # Databases
    "databases": [
        "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis",
        "elasticsearch", "oracle", "mariadb", "cassandra",
    ],
    # Cloud / DevOps
    "devops_cloud": [
        "docker", "kubernetes", "git", "github", "gitlab", "ci/cd",
        "jenkins", "aws", "azure", "gcp", "linux", "nginx", "apache",
        "terraform", "ansible",
    ],
    # Scraping
    "scraping": [
        "scrapy", "beautifulsoup", "selenium", "playwright",
        "requests", "lxml", "puppeteer",
    ],
    # Soft skills (French + English)
    "soft_skills": [
        "communication", "travail en équipe", "teamwork", "leadership",
        "autonomie", "autonomy", "adaptabilité", "adaptability",
        "résolution de problèmes", "problem solving", "créativité",
        "creativity", "organisation", "rigueur",
    ],
}
 
# Flat set for fast lookup
ALL_SKILLS_FLAT: set = {
    skill.lower()
    for skills_list in TECHNICAL_SKILLS.values()
    for skill in skills_list
}
 
# ──────────────────────────────────────────────
# Extra stop words (domain-specific)
# ──────────────────────────────────────────────
EXTRA_STOP_WORDS = {
    "cv", "curriculum", "vitae", "profil", "profile", "nom", "prénom",
    "adresse", "téléphone", "email", "date", "naissance", "nationalité",
    "experience", "expérience", "formation", "education", "compétence",
    "competence", "skill", "langue", "language", "intérêt", "interet",
    "projet", "project", "certification", "references", "référence",
}
 
 
# ──────────────────────────────────────────────
# Core NLP functions
# ──────────────────────────────────────────────
 
def tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokeniser."""
    tokens = re.findall(r"\b\w[\w.+#-]*\b", text.lower())
    return tokens
 
 
def remove_stop_words(tokens: List[str], extra: bool = True) -> List[str]:
    """Remove spaCy stop words + optional domain-specific extras."""
    spacy_stops = nlp.Defaults.stop_words
    filtered = [
        t for t in tokens
        if t not in spacy_stops
        and (not extra or t not in EXTRA_STOP_WORDS)
        and len(t) > 1
    ]
    return filtered
 
 
def lemmatize(tokens: List[str]) -> List[str]:
    """Lemmatise a list of tokens using spaCy."""
    doc = nlp(" ".join(tokens))
    return [token.lemma_.lower() for token in doc if not token.is_space]
 
 
def preprocess_text(text: str, do_lemmatize: bool = True) -> List[str]:
    """
    Full NLP preprocessing pipeline:
      text → lowercase tokens → stop word removal → lemmatisation
    Returns a cleaned list of tokens.
    """
    tokens = tokenize(text)
    tokens = remove_stop_words(tokens)
    if do_lemmatize:
        tokens = lemmatize(tokens)
    return tokens
 
 
def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Detect technical skills mentioned in text using the dictionary.
    Returns a dict  {category: [matched_skills]}.
    """
    text_lower = text.lower()
    found: Dict[str, List[str]] = {}
 
    for category, skills in TECHNICAL_SKILLS.items():
        matched = []
        for skill in skills:
            # Use word-boundary matching for short skill names
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                matched.append(skill)
        if matched:
            found[category] = matched
 
    return found
 
 
def extract_skills_flat(text: str) -> List[str]:
    """Return a flat deduplicated list of all detected skills."""
    found = extract_skills_from_text(text)
    return list({skill for skills in found.values() for skill in skills})
 
 
def preprocess_for_tfidf(text: str) -> str:
    """
    Preprocess text and return a single clean string suitable for
    TF-IDF vectorisation (tokens joined by spaces).
    """
    tokens = preprocess_text(text)
    return " ".join(tokens)
    