import os, django, sys, requests, re, time
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scraping.models import JobOffer

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

HARD_SKILLS = [
    'python', 'java', 'javascript', 'php', 'sql', 'react', 'django',
    'html', 'css', 'machine learning', 'deep learning', 'git', 'docker',
    'linux', 'mysql', 'mongodb', 'pandas', 'numpy', 'power bi', 'tableau',
    'spark', 'hadoop', 'tensorflow', 'keras', 'scikit-learn', 'r studio',
    'angular', 'vue', 'node', 'spring', 'laravel', 'postgresql', 'oracle',
    'aws', 'azure', 'devops', 'kotlin', 'swift', 'flutter', 'excel', 'vba',
]

SOFT_SKILLS = [
    'communication', 'leadership', 'travail en équipe', 'teamwork',
    'gestion de projet', 'project management', 'créativité', 'autonomie',
    'organisation', 'rigueur', 'adaptabilité', 'esprit d\'analyse',
    'sens des responsabilités', 'polyvalence', 'proactivité',
]

SECTEURS = {
    'informatique': ['informatique', 'it', 'digital', 'logiciel', 'software', 'web', 'data', 'cloud', 'réseau', 'télécommunication'],
    'finance': ['finance', 'comptabilité', 'audit', 'banque', 'assurance', 'contrôle de gestion'],
    'marketing': ['marketing', 'communication', 'commercial', 'vente', 'business development'],
    'rh': ['ressources humaines', 'rh', 'recrutement', 'formation', 'paie'],
    'ingénierie': ['ingénieur', 'génie civil', 'mécanique', 'électrique', 'industriel'],
    'santé': ['santé', 'médecin', 'pharmacie', 'biologie', 'médical'],
    'logistique': ['logistique', 'supply chain', 'transport', 'achat'],
}

def detecter_secteur(texte):
    texte_lower = texte.lower()
    for secteur, mots in SECTEURS.items():
        if any(m in texte_lower for m in mots):
            return secteur.capitalize()
    return "Autre"

def extraire_skills(texte):
    t = texte.lower()
    hard = [s for s in HARD_SKILLS if s in t]
    soft = [s for s in SOFT_SKILLS if s in t]
    return hard, soft

def extraire_experience(texte):
    patterns = [
        r'(\d+)\s*[\-à]\s*(\d+)\s*ans?',
        r'(\d+)\s*ans?\s*d.expérience',
        r'minimum\s*(\d+)\s*ans?',
        r'au moins\s*(\d+)\s*ans?',
    ]
    for p in patterns:
        m = re.search(p, texte.lower())
        if m:
            return m.group(0)
    return "Non précisé"

def get_details_rekrute(url_offre):
    try:
        time.sleep(1.5)
        r = requests.get(url_offre, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        # ✅ Entreprise depuis l'URL
        entreprise = "Non précisé"
        url_match = re.search(r'recrutement-(.+?)-\d+\.html', url_offre)
        if url_match:
            parts = url_match.group(1).split('-')
            entreprise = ' '.join(parts[:-1]).title()

        # ✅ Secteur depuis h2
        secteur = "Autre"
        h2 = soup.find('h2')
        if h2 and h2.text.strip():
            secteur = h2.text.strip()
        else:
            secteur = detecter_secteur(r.text)

        # Description
        description = ""
        for cls in ['detailsOffre', 'jobDescription', 'details', 'description']:
            t = soup.find('div', class_=cls)
            if t:
                description = t.get_text(separator=' ').strip()
                break
        if not description:
            main = soup.find('div', class_='col-md-8') or soup.find('main')
            if main:
                description = main.get_text(separator=' ').strip()[:3000]

        experience = extraire_experience(description)
        hard, soft = extraire_skills(description)
        all_skills = [f"[Hard] {s}" for s in hard] + [f"[Soft] {s}" for s in soft]

        return entreprise, description, all_skills, experience, secteur

    except Exception as e:
        print(f"    Erreur détail : {e}")
        return "Non précisé", "", [], "Non précisé", "Autre"


def scrape_rekrute(keyword="informatique", pages=2):
    total = 0
    print(f"\n🔵 SCRAPING REKRUTE — '{keyword}'")
    for page in range(1, pages + 1):
        url = f"https://www.rekrute.com/offres.html?s={keyword}&p={page}"
        print(f"📄 Page {page}/{pages}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            annonces = soup.find_all('li', class_='post-id')
            print(f"   → {len(annonces)} offres trouvées")

            for annonce in annonces:
                try:
                    titre_tag = annonce.find('a', class_='titreJob')
                    if not titre_tag:
                        h2 = annonce.find('h2')
                        titre_tag = h2.find('a') if h2 else None
                    if not titre_tag:
                        continue

                    titre = titre_tag.text.strip()
                    url_offre = "https://www.rekrute.com" + titre_tag['href']

                    localisation = "Non précisé"
                    if "|" in titre:
                        p = titre.split("|")
                        titre = p[0].strip()
                        localisation = p[1].strip()

                    if localisation == "Non précisé":
                        loc_tag = annonce.find('span', class_='location') or \
                                  annonce.find('li', class_='location')
                        if loc_tag:
                            localisation = loc_tag.text.strip()

                    contrat = "Autre"
                    for c in ['CDI', 'CDD', 'Stage', 'Freelance']:
                        if c.lower() in annonce.text.lower():
                            contrat = c
                            break

                    print(f"    ⏳ {titre[:45]}...")
                    entreprise, desc, skills, exp, secteur = get_details_rekrute(url_offre)

                    _, created = JobOffer.objects.get_or_create(
                        url=url_offre,
                        defaults={
                            'title': titre,
                            'company': entreprise,
                            'sector': secteur,
                            'location': localisation,
                            'contract': contrat,
                            'description': desc,
                            'experience': exp,
                            'skills': skills,
                            'source': 'rekrute',
                        }
                    )
                    if created:
                        total += 1
                        print(f"    ✅ Sauvegardé : {titre[:40]}")
                    else:
                        print(f"    ⏭️  Déjà en base")

                except Exception as e:
                    print(f"    ❌ Erreur offre : {e}")

        except Exception as e:
            print(f"  ❌ Erreur page {page} : {e}")

    return total


def scrape_emploima(keyword="informatique", pages=3):
    total = 0
    print(f"\n🟢 SCRAPING EMPLOI.MA — '{keyword}'")

    for page in range(1, pages + 1):
        url = f"https://www.emploi.ma/recherche-jobs-maroc?search%5Bkeywords%5D={keyword}&page={page}"
        print(f"📄 Page {page}/{pages}")
        try:
            time.sleep(2)
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            # ✅ Bonne classe trouvée
            annonces = soup.find_all('div', class_='card-job')
            print(f"   → {len(annonces)} offres trouvées")

            if not annonces:
                print(f"   ⚠️ Aucune offre")
                continue

            for annonce in annonces:
                try:
                    # Titre
                    titre_tag = annonce.find('a', class_='card-job-title') or \
                                annonce.find('h2') or \
                                annonce.find('h3') or \
                                annonce.find('a')
                    if not titre_tag:
                        continue
                    titre = titre_tag.text.strip()

                    # URL
                    lien = annonce.find('a')
                    if not lien or not lien.get('href'):
                        continue
                    href = lien['href']
                    url_offre = href if href.startswith('http') else "https://www.emploi.ma" + href

                    # ✅ Entreprise
                    entreprise = "Non précisé"
                    company_tag = annonce.find('a', class_='company-name') or \
                                  annonce.find(class_='card-job-company')
                    if company_tag:
                        entreprise = company_tag.text.strip()

                    # ✅ Localisation
                    localisation = "Non précisé"
                    loc_tag = annonce.find(class_='card-job-location') or \
                              annonce.find(class_='location')
                    if loc_tag:
                        localisation = loc_tag.text.strip()

                    # Description
                    desc_tag = annonce.find('div', class_='card-job-description')
                    desc = desc_tag.text.strip()[:1000] if desc_tag else annonce.text.strip()[:500]

                    # Contrat
                    contrat = "Autre"
                    for c in ['CDI', 'CDD', 'Stage', 'Freelance']:
                        if c.lower() in annonce.text.lower():
                            contrat = c
                            break

                    # Skills + Secteur + Expérience
                    hard, soft = extraire_skills(desc)
                    all_skills = [f"[Hard] {s}" for s in hard] + [f"[Soft] {s}" for s in soft]
                    secteur = detecter_secteur(desc)
                    experience = extraire_experience(desc)

                    print(f"    ✅ {titre[:40]} | {entreprise[:20]} | {localisation}")

                    _, created = JobOffer.objects.get_or_create(
                        url=url_offre,
                        defaults={
                            'title': titre,
                            'company': entreprise,
                            'sector': secteur,
                            'location': localisation,
                            'contract': contrat,
                            'description': desc,
                            'experience': experience,
                            'skills': all_skills,
                            'source': 'emploima',
                        }
                    )
                    if created:
                        total += 1

                except Exception as e:
                    print(f"   ❌ Erreur offre : {e}")

        except Exception as e:
            print(f"  ❌ Erreur page {page} : {e}")

    return total

if __name__ == "__main__":
    keywords = ["informatique", "data science", "développeur", "marketing", "finance"]

    print("🗑️  Suppression des anciennes offres...")
    JobOffer.objects.all().delete()

    total = 0
    for kw in keywords:
        total += scrape_rekrute(keyword=kw, pages=2)
        time.sleep(2)
        total += scrape_emploima(keyword=kw, pages=2)
        time.sleep(2)

    print(f"\n{'='*50}")
    print(f"✅ TOTAL : {total} offres sauvegardées")
    print(f"   En base : {JobOffer.objects.count()} offres")
    print(f"{'='*50}")