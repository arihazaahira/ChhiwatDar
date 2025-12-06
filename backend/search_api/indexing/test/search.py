import json
import os

def charger_index(chemin_fichier):
    """Charge le fichier JSON en mémoire."""
    if not os.path.exists(chemin_fichier):
        print(f"Erreur : Le fichier '{chemin_fichier}' n'existe pas.")
        return None
    
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        return json.load(f)

def rechercher(index, requete):
    """Cherche un ou plusieurs mots dans l'index."""
    # On nettoie la requête (minuscule + suppression espaces)
    mots_cles = requete.lower().strip().split()
    
    resultats = {}

    for mot in mots_cles:
        docs = index.get(mot)
        if docs:
            resultats[mot] = docs
        else:
            resultats[mot] = ["Aucun résultat"]
            
    return resultats

# --- Programme Principal ---

NOM_FICHIER = 'inverted_index.json' # Assure-toi que c'est le bon nom

print("Chargement de l'index...")
index = charger_index(NOM_FICHIER)

if index:
    while True:
        print("\n" + "-"*30)
        user_input = input("Entrez votre requête (ou 'q' pour quitter) : ")
        
        if user_input.lower() == 'q':
            break
        
        res = rechercher(index, user_input)
        
        # Affichage propre des résultats
        for mot, docs in res.items():
            print(f"Terme '{mot}' trouvé dans : {docs}")