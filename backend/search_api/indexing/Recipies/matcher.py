import json
import os
from difflib import get_close_matches

# === Localisation correcte de inverted_index.json ===

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INVERTED_INDEX_PATH = os.path.join(CURRENT_DIR, "inverted_index.json")

# Charger l'index au chargement du module
with open(INVERTED_INDEX_PATH, "r", encoding="utf-8") as f:
    INVERTED_INDEX = json.load(f)


def find_recipes_by_ingredients(ingredients):
    """
    Retourne (filename, score) pour chaque recette contenant ces ingrédients.
    """
    scores = {}

    for ing in ingredients:
        term = ing.lower().strip()
        if term in INVERTED_INDEX:
            files = INVERTED_INDEX[term]
            for f in files:
                scores[f] = scores.get(f, 0) + 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def find_recipes_by_name(name):
    """
    Fuzzy match sur le nom de la recette prédite par Gemini.
    """
    name = name.lower().strip()

    terms = list(INVERTED_INDEX.keys())
    match = get_close_matches(name, terms, n=1, cutoff=0.7)

    if not match:
        return []
    
    return INVERTED_INDEX[match[0]]


def match_recipe(name_recette, ingredients):
    """
    Combinaison des deux signaux : nom + ingrédients.
    """
    final_scores = {}

    # Score du nom
    for f in find_recipes_by_name(name_recette):
        final_scores[f] = final_scores.get(f, 0) + 5

    # Score des ingrédients
    for f, s in find_recipes_by_ingredients(ingredients):
        final_scores[f] = final_scores.get(f, 0) + s

    ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked
