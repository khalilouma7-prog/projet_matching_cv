import requests
from bs4 import BeautifulSoup
import json # On ajoute json pour voir à quoi ressembleront nos données finales

url = "https://www.rekrute.com/offres.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

titres_annonces = soup.find_all('h2')

# On crée une liste vide qui va stocker nos offres nettoyées
donnees_offres = []

for titre in titres_annonces[:5]:
    balise_lien = titre.find('a')
    
    if balise_lien:
        texte_complet = titre.text.strip()
        url_offre = "https://www.rekrute.com" + balise_lien['href']
        
        # Le nettoyage : on sépare le titre et la ville avec split()
        morceaux = texte_complet.split('|')
        if len(morceaux) == 2:
            titre_offre = morceaux[0].strip()
            lieu_offre = morceaux[1].strip()
        else:
            titre_offre = texte_complet
            lieu_offre = "Non précisé"
            
        # On range les informations dans un "dictionnaire" Python
        offre_propre = {
            "titre": titre_offre,
            "localisation": lieu_offre,
            "url": url_offre
        }
        
        # On ajoute cette offre propre à notre liste
        donnees_offres.append(offre_propre)

# On affiche le résultat de manière structurée
print("✅ Extraction terminée ! Voici vos données formatées :\n")
print(json.dumps(donnees_offres, indent=4, ensure_ascii=False))