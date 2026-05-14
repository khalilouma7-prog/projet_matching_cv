import os, django, sys, requests, re, time
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scraping.models import JobOffer

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

COMPETENCES = [
    'python', 'java', 'javascript', 'php', 'sql', 'react', 'django',
    'html', 'css', 'machine learning', 'excel', 'git', 'docker', 'linux',
    'mysql', 'mongodb', 'pandas', 'numpy', 'power bi', 'spark',
]

def extraire_competences(texte):
    return [c for c in COMPETENCES if c in texte.lower()]

def get_details_rekrute(url_offre):
    try:
        time.sleep(2)
        r = requests.get(url_offre, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        entreprise = "Non précisé"
        for tag, cls in [('a','nameEts'),('span','company'),('div','company-name')]:
            t = soup.find(tag, class_=cls)
            if t: entreprise = t.text.strip(); break

        description = ""
        for cls in ['detailsOffre','jobDescription','details','description']:
            t = soup.find('div', class_=cls)
            if t: description = t.text.strip(); break
        if not description:
            main = soup.find('div', class_='col-md-8') or soup.find('main')
            if main: description = main.text.strip()[:2000]

        experience = 0
        m = re.search(r'(\d+)\s*(an|année)', description.lower())
        if m: experience = int(m.group(1))

        return entreprise, description, extraire_competences(description), experience
    except Exception as e:
        print(f"    Erreur : {e}")
        return "Non précisé", "", [], 0


def scrape_rekrute(keyword="informatique", pages=2):
    total = 0
    print("\n🔵 SCRAPING REKRUTE")
    for page in range(1, pages + 1):
        url = f"https://www.rekrute.com/offres.html?s={keyword}&p={page}"
        print(f"📄 Page {page}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            annonces = soup.find_all('li', class_='post-id')
            print(f"   → {len(annonces)} offres")

            for annonce in annonces:
                try:
                    titre_tag = annonce.find('a', class_='titreJob')
                    if not titre_tag:
                        h2 = annonce.find('h2')
                        titre_tag = h2.find('a') if h2 else None
                    if not titre_tag: continue

                    titre = titre_tag.text.strip()
                    url_offre = "https://www.rekrute.com" + titre_tag['href']

                    localisation = "Non précisé"
                    if "|" in titre:
                        p = titre.split("|")
                        titre = p[0].strip()
                        localisation = p[1].strip()

                    contrat = "Autre"
                    for c in ['CDI','CDD','Stage','Freelance']:
                        if c.lower() in annonce.text.lower():
                            contrat = c; break

                    entreprise, desc, skills, exp = get_details_rekrute(url_offre)

                    _, created = JobOffer.objects.get_or_create(
                        url=url_offre,
                        defaults={
                            'title': titre,
                            'company': entreprise,
                            'location': localisation,
                            'contract': contrat,
                            'description': desc,
                            'experience': str(exp),
                            'skills': skills,
                            'source': 'rekrute',
                        }
                    )
                    if created: total += 1; print(f"    ✅ {titre[:40]}")

                except Exception as e:
                    print(f"    Erreur offre : {e}")
        except Exception as e:
            print(f"    Erreur page : {e}")
    return total


if __name__ == "__main__":
    print("🗑️  Suppression des anciennes offres...")
    JobOffer.objects.all().delete()

    total = scrape_rekrute(keyword="informatique", pages=3)

    print(f"\n✅ TOTAL : {total} offres sauvegardées")
    print(f"   En base : {JobOffer.objects.count()} offres")