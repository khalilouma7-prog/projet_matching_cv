import os
import django
import sys
import requests
import re
import time
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from jobs.models import Offre

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

COMPETENCES = [
    'python', 'java', 'javascript', 'php', 'sql', 'react',
    'django', 'html', 'css', 'machine learning', 'excel',
    'git', 'docker', 'linux', 'mysql', 'mongodb', 'pandas',
    'numpy', 'power bi', 'tableau', 'spark', 'hadoop',
    'communication', 'leadership', 'gestion de projet', 'anglais'
]

def extraire_competences_texte(texte):
    texte_lower = texte.lower()
    return [c for c in COMPETENCES if c in texte_lower]

# ════════════════════════════════════════
# SCRAPER 1 : REKRUTE
# ════════════════════════════════════════

def get_details_rekrute(url_offre):
    try:
        time.sleep(2)  # ← Délai pour éviter le blocage
        response = requests.get(url_offre, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ── Entreprise ──
        entreprise = "Non précisé"
        for selector in [
            ('a', 'nameEts'),
            ('span', 'company'),
            ('div', 'company-name'),
        ]:
            tag = soup.find(selector[0], class_=selector[1])
            if tag:
                entreprise = tag.text.strip()
                break

        # ── Description ──
        description = ""
        for selector in ['detailsOffre', 'jobDescription', 'details', 'description']:
            tag = soup.find('div', class_=selector)
            if tag:
                description = tag.text.strip()
                break

        # Si toujours vide, prendre tout le contenu principal
        if not description:
            main = soup.find('div', class_='col-md-8') or soup.find('main')
            if main:
                description = main.text.strip()[:2000]

        # ── Expérience ──
        experience = 0
        exp_match = re.search(r'(\d+)\s*(an|année)', description.lower())
        if exp_match:
            experience = int(exp_match.group(1))

        # ── Compétences ──
        competences = extraire_competences_texte(description)

        return entreprise, description, competences, experience

    except Exception as e:
        print(f"    Erreur détail Rekrute : {e}")
        return "Non précisé", "", [], 0


def scrape_rekrute(keyword="informatique", pages=3):
    offres_sauvegardees = 0
    print("\n" + "="*50)
    print("🔵 SCRAPING REKRUTE")
    print("="*50)

    for page in range(1, pages + 1):
        url = f"https://www.rekrute.com/offres.html?s={keyword}&p={page}"
        print(f"\n📄 Page {page} : {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            annonces = soup.find_all('li', class_='post-id')
            print(f"   → {len(annonces)} offres trouvées")

            for annonce in annonces:
                try:
                    # ── Titre + URL ──
                    titre_tag = annonce.find('a', class_='titreJob')
                    if not titre_tag:
                        h2 = annonce.find('h2')
                        titre_tag = h2.find('a') if h2 else None

                    if not titre_tag:
                        continue

                    titre = titre_tag.text.strip()
                    url_offre = "https://www.rekrute.com" + titre_tag['href']

                    # ── Localisation depuis le titre ──
                    localisation = "Non précisé"
                    if "|" in titre:
                        parties = titre.split("|")
                        titre = parties[0].strip()
                        localisation = parties[1].strip()

                    # ── Type contrat ──
                    type_contrat = "Non précisé"
                    texte = annonce.text
                    for contrat in ['CDI', 'CDD', 'Stage', 'Freelance']:
                        if contrat.lower() in texte.lower():
                            type_contrat = contrat
                            break

                    # ── Détails depuis la page de l'offre ──
                    print(f"    Chargement détails : {titre[:40]}...")
                    entreprise, description, competences, experience = get_details_rekrute(url_offre)

                    print(f"    {titre[:35]} | {localisation} | {entreprise} | {type_contrat}")
                    print(f"      Compétences: {competences}")

                    # ── Sauvegarde ──
                    offre, created = Offre.objects.get_or_create(
                        url_source=url_offre,
                        defaults={
                            'titre': titre,
                            'entreprise': entreprise,
                            'localisation': localisation,
                            'type_contrat': type_contrat,
                            'description': description,
                            'experience_requise': experience,
                            'competences_requises': competences,
                        }
                    )
                    if created:
                        offres_sauvegardees += 1

                except Exception as e:
                    print(f"    Erreur offre : {e}")
                    continue

        except Exception as e:
            print(f"    Erreur page : {e}")
            continue

    return offres_sauvegardees


# ════════════════════════════════════════
# SCRAPER 2 : EMPLOI.MA
# ════════════════════════════════════════

def scrape_emploima(keyword="informatique", pages=2):
    offres_sauvegardees = 0
    print("\n" + "="*50)
    print("🟢 SCRAPING EMPLOI.MA")
    print("="*50)

    for page in range(1, pages + 1):
        url = f"https://www.emploi.ma/recherche-jobs-maroc?search={keyword}&page={page}"
        print(f"\n📄 Page {page} : {url}")

        try:
            time.sleep(1)
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            annonces = soup.find_all('div', class_='job-description-wrapper')
            print(f"   → {len(annonces)} offres trouvées")

            for annonce in annonces:
                try:
                    # ── Titre ──
                    titre_tag = annonce.find('h5') or annonce.find('h3') or annonce.find('h2')
                    if not titre_tag:
                        continue
                    titre = titre_tag.text.strip()

                    # ── URL ──
                    lien = annonce.find('a')
                    url_offre = ""
                    if lien and lien.get('href'):
                        href = lien['href']
                        url_offre = href if href.startswith('http') else "https://www.emploi.ma" + href

                    # ── Entreprise ──
                    entreprise = "Non précisé"
                    for cls in ['company', 'entreprise', 'recruiter']:
                        tag = annonce.find(class_=lambda c: c and cls in c.lower() if c else False)
                        if tag:
                            entreprise = tag.text.strip()
                            break

                    # ── Localisation ──
                    localisation = "Non précisé"
                    for cls in ['location', 'ville', 'city']:
                        tag = annonce.find(class_=lambda c: c and cls in c.lower() if c else False)
                        if tag:
                            localisation = tag.text.strip()
                            break

                    # ── Description ──
                    description = annonce.text.strip()[:1000]

                    # ── Compétences ──
                    competences = extraire_competences_texte(description)

                    # ── Type contrat ──
                    type_contrat = "Non précisé"
                    for contrat in ['CDI', 'CDD', 'Stage', 'Freelance']:
                        if contrat.lower() in description.lower():
                            type_contrat = contrat
                            break

                    print(f"    {titre[:35]} | {localisation} | {entreprise}")

                    if url_offre:
                        offre, created = Offre.objects.get_or_create(
                            url_source=url_offre,
                            defaults={
                                'titre': titre,
                                'entreprise': entreprise,
                                'localisation': localisation,
                                'type_contrat': type_contrat,
                                'description': description,
                                'experience_requise': 0,
                                'competences_requises': competences,
                            }
                        )
                        if created:
                            offres_sauvegardees += 1

                except Exception as e:
                    print(f"   Erreur : {e}")
                    continue

        except Exception as e:
            print(f"    Erreur page : {e}")
            continue

    return offres_sauvegardees


# ════════════════════════════════════════
# LANCEMENT
# ════════════════════════════════════════

if __name__ == "__main__":
    print("🗑️  Suppression des anciennes offres...")
    Offre.objects.all().delete()

    total = 0
    total += scrape_rekrute(keyword="informatique", pages=2)
    total += scrape_emploima(keyword="informatique", pages=2)

    print(f"\n{'='*50}")
    print(f" TOTAL : {total} nouvelles offres sauvegardées")
    print(f" Total en base : {Offre.objects.count()} offres")
    print(f"{'='*50}")