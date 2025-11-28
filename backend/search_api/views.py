import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Charger les données une fois au démarrage
def load_recipes_data():
    file_path = os.path.join(os.path.dirname(__file__), '../data/recipes.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

recipes_data = load_recipes_data()

@require_http_methods(["GET"])
def get_all_recipes(request):
    """Retourne toutes les recettes"""
    return JsonResponse(recipes_data, safe=False)

@require_http_methods(["GET"])
def search_recipes(request):
    """Recherche des recettes par mot-clé"""
    query = request.GET.get('query', '').lower().strip()
    
    if not query:
        return JsonResponse([], safe=False)
    
    # Recherche dans les titres et descriptions
    results = []
    for recipe in recipes_data:
        title_match = query in recipe.get('title', '').lower()
        description_match = query in recipe.get('description', '').lower()
        ingredients_match = any(query in ingredient.lower() for ingredient in recipe.get('ingredients', []))
        
        if title_match or description_match or ingredients_match:
            results.append(recipe)
    
    return JsonResponse(results, safe=False)

@require_http_methods(["GET"])
def get_recipe_details(request, recipe_id):
    """Retourne les détails d'une recette spécifique"""
    try:
        recipe = next((r for r in recipes_data if r['id'] == recipe_id), None)
        if recipe:
            return JsonResponse(recipe)
        else:
            return JsonResponse({'error': 'Recette non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)