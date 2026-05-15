#  CV & Offres Matching Platform

> Plateforme intelligente d'analyse de compatibilité CV/Offres d'emploi par Data Mining  
> Licence IASD — Module Data Mining 2025/2026

---

##  Table des Matières

- [Description](#description)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Scraping](#scraping)
- [Structure du projet](#structure-du-projet)
- [API Endpoints](#api-endpoints)
- [Algorithme de Matching](#algorithme-de-matching)
- [Équipe](#équipe)

---

##  Description

CV&Match est une plateforme web intelligente qui permet à un utilisateur de :

- **Uploader son CV** (PDF ou DOCX)
- **Matcher automatiquement** son profil avec des offres d'emploi scrapées
- **Visualiser** les résultats avec des graphiques interactifs (RadarChart, WordCloud, Carte géo)
- **Analyser** la répartition des offres par domaine (K-Means clustering)

### Fonctionnalités principales

| Module | Description |
|--------|-------------|
|  Authentification | Inscription, connexion, gestion profil |
|  Scraping | Collecte automatique Rekrute + Emploi.ma |
|  NLP | Extraction features CV (spaCy + TF-IDF) |
|  Matching | Score pondéré (Cosinus + Jaccard + Exp + Géo) |
|  Dashboard | Visualisations interactives |

---

##  Architecture

```
projet_matching_cv/
├── backend/                    # Django 5.2 (API REST)
│   ├── backend/                # Config (settings, urls, wsgi)
│   ├── users/                  # Auth + Profil utilisateur
│   ├── scraping/               # Modèle JobOffer + scripts
│   ├── nlp_engine/             # NLP (spaCy, TF-IDF, extraction)
│   ├── matching/               # Moteur de matching + K-Means
│   ├── results/                # Résultats + Dashboard stats
│   ├── scraper_rekrute.py      # Script de scraping
│   └── manage.py
│
└── frontend/                   # React 18 + Vite
    └── src/
        ├── pages/              # Login, Register, Dashboard, Results, Profile
        ├── components/         # Sidebar, Topbar, ScoreRing, RadarChart...
        └── services/           # api.js (Axios)
```

---

##  Prérequis

### Backend
- Python 3.10+
- pip
- virtualenv

### Frontend
- Node.js 18+
- npm

---

##  Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/khalilouma7-prog/projet_matching_cv.git
cd projet_matching_cv
```

### 2. Backend — Créer l'environnement virtuel

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Backend — Installer les dépendances

```bash
pip install django djangorestframework django-cors-headers
pip install scikit-learn pandas numpy spacy
pip install pdfplumber python-docx requests beautifulsoup4
pip install djangorestframework-simplejwt Pillow
```

### 4. Installer le modèle spaCy français

```bash
python -m spacy download fr_core_news_sm
```

### 5. Frontend — Installer les dépendances

```bash
cd ../frontend
npm install
```

---

## 🔧 Configuration

### `backend/backend/settings.py`

Vérifiez que ces paramètres sont présents :

```python
# Modèle User personnalisé
AUTH_USER_MODEL = 'users.User'

# CORS pour React
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True

# Sessions
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = False

# Fichiers media (CVs uploadés)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

##  Lancement

### 1. Migrations de la base de données

```bash
cd backend
python manage.py makemigrations users scraping nlp_engine matching results
python manage.py migrate
```

### 2. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 3. Lancer le backend

```bash
python manage.py runserver
```

> Le backend tourne sur `http://localhost:8000`

### 4. Lancer le frontend

```bash
cd ../frontend
npm run dev
```

> Le frontend tourne sur `http://localhost:5173`

---

##  Scraping

### Lancer le scraper (depuis le dossier backend)

```bash
cd backend
python scraper_rekrute.py
```

Le scraper collecte des offres depuis :
- **Rekrute.com** — mots-clés : informatique, data science, développeur, marketing, finance
- **Emploi.ma** — mêmes mots-clés

### Vérifier les offres en base

```bash
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from scraping.models import JobOffer
print(f'Total offres : {JobOffer.objects.count()}')
"
```

### Supprimer et rescaper

```bash
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from scraping.models import JobOffer
JobOffer.objects.all().delete()
print('Offres supprimées')
"
python scraper_rekrute.py
```

---

##  Structure du projet

### Apps Django

| App | Rôle |
|-----|------|
| `users` | User custom, UserProfile, UploadedCV |
| `scraping` | JobOffer, ScrapingSource |
| `nlp_engine` | CVDocument, CVProfile, SkillVector |
| `matching` | compute_matching, K-Means, scoring |
| `results` | MatchResult, dashboard_stats |

### Pages React

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | Connexion |
| Register | `/register` | Inscription |
| Dashboard | `/dashboard` | Vue globale du marché |
| Mes Résultats | `/results` | Upload CV + matching |
| Mon Profil | `/profile` | Édition profil + historique |

---

##  API Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/users/auth/register/` | Inscription |
| POST | `/api/users/auth/login/` | Connexion |
| GET/PUT | `/api/users/users/<id>/` | Profil utilisateur |
| POST | `/api/matching/match-cv/` | Upload CV + matching |
| GET | `/api/matching/map-offers/` | Points géographiques |
| GET | `/api/results/` | Résultats de matching |
| GET | `/api/results/dashboard-stats/` | Statistiques dashboard |

---

##  Algorithme de Matching

### Formule

```
Score = 0.50 × Cosinus TF-IDF
      + 0.25 × Distance Jaccard
      + 0.15 × Experience Match
      + 0.10 × Geo Match
```

### Pipeline NLP

```
CV (PDF/DOCX)
    → Extraction texte (pdfplumber / python-docx)
    → Nettoyage (regex)
    → Tokenisation (spaCy fr_core_news_sm)
    → Suppression stop words
    → Lemmatisation
    → Vectorisation TF-IDF (max 3000 features)
    → Similarité Cosinus vs offres
```

### Clustering K-Means

```
Descriptions offres
    → Vectorisation TF-IDF
    → K-Means (K optimal par Silhouette Score)
    → Clusters : Informatique, Finance, Marketing, RH...
```

---
<img width="389" height="197" alt="image" src="https://github.com/user-attachments/assets/c0ff35f0-2f7c-4806-a698-84452ce8df4e" />



##  Licence

Projet académique — Licence IASD, Faculté des Sciences Semlalia, Marrakech — 2025/2026
