"""
Views pour l'API de recherche de recettes marocaines
"""

import json
import os
import time
import uuid
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from google import genai
from google.genai import types
from PIL import Image


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

def load_recipes_data():
    """Charge les données des recettes depuis le fichier JSON"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), '../data/recipes.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ Fichier recipes.json introuvable")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du chargement des recettes: {e}")
        return None


def load_user_recipes():
    """Charge les recettes créées par les utilisateurs"""
    try:
        user_recipes_file = os.path.join(os.path.dirname(__file__), '../data/user_recipes.json')
        
        if os.path.exists(user_recipes_file):
            with open(user_recipes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ Erreur chargement recettes utilisateurs: {e}")
        return []


# ============================================================
# ENDPOINTS DE RECHERCHE DE RECETTES
# ============================================================

@require_http_methods(["GET"])
def get_all_recipes(request):
    """Retourne toutes les recettes (officielles + utilisateurs)"""
    recipes_data = load_recipes_data()
    user_recipes = load_user_recipes()
    
    if recipes_data is None:
        return JsonResponse({
            'success': False,
            'error': 'Problème avec le serveur. Impossible de charger les recettes.'
        }, status=500)
    
    # Combiner les deux listes
    all_recipes = recipes_data + user_recipes
    
    return JsonResponse({
        'success': True,
        'recipes': all_recipes
    })


@require_http_methods(["GET"])
def search_recipes(request):
    """Recherche des recettes par mot-clé"""
    query = request.GET.get('query', '').lower().strip()
    
    if not query:
        return JsonResponse({
            'success': True,
            'recipes': []
        })
    
    recipes_data = load_recipes_data()
    user_recipes = load_user_recipes()
    
    if recipes_data is None:
        return JsonResponse({
            'success': False,
            'error': 'Problème avec le serveur. Impossible de rechercher les recettes.'
        }, status=500)
    
    # Combiner toutes les recettes
    all_recipes = recipes_data + user_recipes
    
    # Recherche dans les titres, descriptions et ingrédients
    results = []
    for recipe in all_recipes:
        title_match = query in recipe.get('title', '').lower()
        description_match = query in recipe.get('description', '').lower()
        ingredients_match = any(query in ingredient.lower() for ingredient in recipe.get('ingredients', []))
        
        if title_match or description_match or ingredients_match:
            results.append(recipe)
    
    return JsonResponse({
        'success': True,
        'recipes': results
    })


@require_http_methods(["GET"])
def get_recipe_details(request, recipe_id):
    """Retourne les détails d'une recette spécifique"""
    recipes_data = load_recipes_data()
    user_recipes = load_user_recipes()
    
    if recipes_data is None:
        return JsonResponse({
            'success': False,
            'error': 'Problème avec le serveur. Impossible de charger la recette.'
        }, status=500)
    
    # Chercher dans toutes les recettes
    all_recipes = recipes_data + user_recipes
    recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    
    if recipe:
        return JsonResponse({
            'success': True,
            'recipe': recipe
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Recette non trouvée'
        }, status=404)


# ============================================================
# ANALYSE D'IMAGE AVEC GOOGLE GEMINI
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
def analyze_recipe_image(request):
    """
    Analyse une image de plat marocain avec Google Gemini AI
    et retourne le nom du plat + ingrédients visibles en JSON
    """
    try:
        print("📸 Requête d'analyse d'image reçue")
        
        # Vérification de la présence de l'image
        if 'image' not in request.FILES:
            print("❌ Aucune image dans la requête")
            return JsonResponse({'error': 'Aucune image fournie'}, status=400)
        
        image_file = request.FILES['image']
        print(f"✅ Image reçue: {image_file.name}")
        
        # Chargement de l'image avec PIL
        try:
            image = Image.open(image_file)
            print(f"✅ Image ouverte: {image.size}")
        except Exception as e:
            print(f"❌ Erreur ouverture image: {e}")
            return JsonResponse({'error': f'Erreur ouverture image: {str(e)}'}, status=400)
        
        # Initialisation du client Gemini
        try:
            api_key = "AIzaSyC8IWjx3f6oDHiGy_VyUu-8cM_t1B0FMxU"
            client = genai.Client(api_key=api_key)
            print("✅ Client Gemini initialisé")
        except Exception as e:
            print(f"❌ Erreur initialisation Gemini: {e}")
            return JsonResponse({'error': f'Erreur API Gemini: {str(e)}'}, status=500)
        
        # Prompt pour l'analyse
        prompt = """
        Analyse cette image et renvoie uniquement une **liste JSON** avec :
        1. "nom_recette" : le nom du plat marocain que tu reconnais.
        2. "ingredients_visibles" : une liste des ingrédients que tu vois dans l'image (en anglais).
        
        Réponds uniquement en JSON, pas de texte supplémentaire.
        """
        
        # Appel au modèle Gemini
        try:
            print("🤖 Appel à Gemini...")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image],
                config=types.GenerateContentConfig(response_modalities=['TEXT'])
            )
            print(f"✅ Réponse Gemini reçue: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Erreur appel Gemini: {e}")
            return JsonResponse({'error': f'Erreur appel Gemini: {str(e)}'}, status=500)
        
        # Extraction et parsing de la réponse JSON
        response_text = response.text.strip()
        
        # Nettoyage des balises markdown
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parsing du JSON
        try:
            analysis_result = json.loads(response_text)
            print(f"✅ JSON parsé: {analysis_result}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"Texte reçu: {response_text}")
            analysis_result = {
                'nom_recette': 'Inconnu',
                'ingredients_visibles': [],
                'raw_response': response_text
            }
        
        # Retour de la réponse
        return JsonResponse({
            'success': True,
            'data': analysis_result
        })
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================
# CRÉATION DE RECETTES
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_user_recipe(request):
    """Permet de créer des recettes et les sauvegarder dans user_recipes.json"""
    try:
        print("📝 Requête de création de recette reçue")
        
        # Récupérer les données du formulaire
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        ingredients = request.POST.get('ingredients', '')
        steps = request.POST.get('steps', '')
        user_name = request.POST.get('user_name', 'Chef Anonyme').strip()
        
        print(f"📋 Données reçues: title={title}, user_name={user_name}")
        
        # Validation des champs requis
        if not all([title, description, ingredients, steps]):
            print("❌ Champs manquants")
            return JsonResponse({
                'success': False,
                'error': 'Tous les champs sont requis (titre, description, ingrédients, étapes)'
            }, status=400)
        
        # Parser les JSON des ingrédients et étapes
        try:
            ingredients_list = json.loads(ingredients)
            steps_list = json.loads(steps)
            print(f"✅ Ingrédients: {len(ingredients_list)}, Étapes: {len(steps_list)}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Format des ingrédients ou étapes invalide'
            }, status=400)
        
        # Gérer l'image uploadée
        image_url = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            print(f"📷 Image reçue: {image_file.name}")
            
            # Créer le dossier pour les images
            upload_dir = os.path.join(os.path.dirname(__file__), '../media/user_recipes')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Sauvegarder l'image avec un nom unique
            filename = f"{uuid.uuid4()}_{image_file.name}"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            image_url = f"/media/user_recipes/{filename}"
            print(f"✅ Image sauvegardée: {image_url}")
        
        # Créer l'objet recette
        recipe_data = {
            'id': f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            'title': title,
            'description': description,
            'ingredients': ingredients_list,
            'steps': steps_list,
            'image': image_url,
            'author': {
                'name': user_name
            },
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_created': True
        }
        
        print(f"✅ Recette créée: {recipe_data['id']}")
        
        # Chemin vers le fichier JSON des recettes utilisateurs
        user_recipes_file = os.path.join(os.path.dirname(__file__), '../data/user_recipes.json')
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(user_recipes_file), exist_ok=True)
        
        # Charger les recettes existantes
        user_recipes = load_user_recipes()
        print(f"📚 Recettes existantes: {len(user_recipes)}")
        
        # Ajouter la nouvelle recette
        user_recipes.append(recipe_data)
        
        # Sauvegarder dans le fichier JSON
        with open(user_recipes_file, 'w', encoding='utf-8') as f:
            json.dump(user_recipes, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Recette sauvegardée dans {user_recipes_file}")
        print(f"✅ Nouvelle recette créée par {user_name}: {title}")
        print(f"📊 Total de recettes utilisateurs: {len(user_recipes)}")
        
        return JsonResponse({
            'success': True,
            'recipe': recipe_data,
            'message': 'Recette créée avec succès !'
        })
        
    except Exception as e:
        print(f"❌ Erreur création recette: {e}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Problème avec le serveur. Impossible de créer la recette.'
        }, status=500)


@require_http_methods(["GET"])
def get_user_recipes(request):
    """Récupère toutes les recettes créées par les utilisateurs"""
    user_recipes = load_user_recipes()
    
    return JsonResponse({
        'success': True,
        'recipes': user_recipes
    })