import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Chemin vers votre fichier recipes.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES_FILE = os.path.join(BASE_DIR, 'data', 'recipes.json')

def load_recipes():
    """Charge les recettes depuis le fichier JSON"""
    try:
        with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
            print(f"✅ Fichier chargé: {len(recipes)} recettes trouvées")
            for recipe in recipes:
                print(f"  - {recipe['title']}")
            return recipes
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {RECIPES_FILE}")
        return []
    except Exception as e:
        print(f"❌ Erreur lecture fichier: {e}")
        return []

@csrf_exempt
@require_http_methods(["GET"])
def search_recipes(request):
    """Recherche des recettes par texte"""
    query = request.GET.get('query', '').strip().lower()
    
    # Log de la requête reçue
    print(f"🔍 REQUÊTE RECHERCHE - Terme: '{query}'")
    
    recipes = load_recipes()
    print(f"📊 Total recettes chargées: {len(recipes)}")
    
    if not query:
        print("📤 ENVOI - Toutes les recettes (recherche vide)")
        return JsonResponse(recipes, safe=False)
    
    # Filtrage des recettes avec logs détaillés
    filtered_recipes = []
    print("🔎 Début du filtrage...")
    
    for recipe in recipes:
        title_match = query in recipe['title'].lower()
        desc_match = query in recipe.get('description', '').lower()
        
        print(f"  📝 Vérification: '{recipe['title']}'")
        print(f"    Title match: {title_match}")
        print(f"    Desc match: {desc_match}")
        
        if title_match or desc_match:
            filtered_recipes.append(recipe)
            print(f"    ✅ AJOUTÉ à résultats")
    
    print(f"📤 ENVOI RECHERCHE - {len(filtered_recipes)} résultat(s) pour '{query}'")
    
    return JsonResponse(filtered_recipes, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def recipe_list(request):
    """Retourne toutes les recettes"""
    print("📥 REQUÊTE LISTE COMPLÈTE")
    
    recipes = load_recipes()
    print(f"📤 ENVOI LISTE - {len(recipes)} recette(s)")
    
    return JsonResponse(recipes, safe=False)