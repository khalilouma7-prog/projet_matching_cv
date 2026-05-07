import re
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

COMPETENCES_CONNUES = [
    'python', 'java', 'javascript', 'php', 'sql', 'react',
    'django', 'html', 'css', 'machine learning', 'excel',
    'git', 'docker', 'linux', 'mysql', 'mongodb', 'pandas',
    'numpy', 'power bi', 'communication', 'leadership', 'gestion de projet'
]

STOP_WORDS_FR = [
    'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et',
    'en', 'à', 'au', 'aux', 'est', 'sont', 'avec', 'pour',
    'par', 'sur', 'dans', 'qui', 'que', 'se', 'ce', 'mon',
    'nous', 'vous', 'ils', 'je', 'tu', 'il', 'son', 'sa', 'ses'
]

def extraire_texte_cv(chemin_cv):
    texte = ""
    try:
        if chemin_cv.endswith('.pdf'):
            with open(chemin_cv, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    texte += page.extract_text() or ""
        elif chemin_cv.endswith('.docx'):
            doc = docx.Document(chemin_cv)
            for para in doc.paragraphs:
                texte += para.text + " "
    except Exception as e:
        print(f" Erreur extraction CV : {e}")
    return texte

def nettoyer_texte(texte):
    texte = texte.lower()
    texte = re.sub(r'[^a-zàâçéèêëîïôûùüÿñæœ\s]', ' ', texte)
    mots = texte.split()
    mots = [m for m in mots if m not in STOP_WORDS_FR and len(m) > 2]
    return " ".join(mots)

def extraire_competences(texte):
    texte_lower = texte.lower()
    return [c for c in COMPETENCES_CONNUES if c in texte_lower]

def calculer_score(cv_texte, offre_description, cv_competences,
                   offre_competences, cv_experience, offre_experience,
                   cv_localisation, offre_localisation):

    # ── Score 1 : Cosinus TF-IDF (50%) ──
    cv_propre = nettoyer_texte(cv_texte)
    offre_propre = nettoyer_texte(offre_description)

    if cv_propre and offre_propre:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([cv_propre, offre_propre])
        sim_cosinus = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    else:
        sim_cosinus = 0.0

    # ── Score 2 : Jaccard compétences (25%) ──
    cv_set = set(cv_competences)
    offre_set = set(offre_competences)
    if cv_set | offre_set:
        jaccard = len(cv_set & offre_set) / len(cv_set | offre_set)
    else:
        jaccard = 0.0

    # ── Score 3 : Expérience (15%) ──
    if offre_experience == 0:
        exp_match = 1.0
    elif cv_experience >= offre_experience:
        exp_match = 1.0
    else:
        exp_match = cv_experience / offre_experience

    # ── Score 4 : Localisation (10%) ──
    geo_match = 1.0 if cv_localisation.lower() in offre_localisation.lower() else 0.0

    # ── Score Final ──
    score = (0.5 * sim_cosinus +
             0.25 * jaccard +
             0.15 * exp_match +
             0.10 * geo_match)

    return {
        'score_total': round(score * 100, 2),
        'score_cosinus': round(sim_cosinus * 100, 2),
        'score_jaccard': round(jaccard * 100, 2),
        'score_experience': round(exp_match * 100, 2),
        'score_geo': round(geo_match * 100, 2),
    }

def clustering_offres(descriptions, n_clusters=3):
    descriptions = [d for d in descriptions if d.strip()]
    if len(descriptions) < n_clusters:
        return [0] * len(descriptions)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(tfidf_matrix)
    return kmeans.labels_.tolist()