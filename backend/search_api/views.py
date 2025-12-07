"""
Views pour l'API de recherche de recettes marocaines avec Inverted Index
(Version finale avec correction du chemin d'accès aux fichiers et amélioration du filtrage des mots-clés)
"""

import json
import os
import time
import uuid
import traceback
import re
import unicodedata
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import google.generativeai as genai
from PIL import Image
from .voice_search.speech_to_text import transcribe


# ============================================================
# CONSTANTES ET CONFIGURATION
# ============================================================

# Chemins des fichiers
# Remarque : BASE_DIR est le dossier 'image_search' dans votre architecture
BASE_DIR = os.path.dirname(__file__) 
RECIPES_JSON_PATH = os.path.join(BASE_DIR, '../data/recipes.json')
USER_RECIPES_PATH = os.path.join(BASE_DIR, '../data/user_recipes.json')
INVERTED_INDEX_PATHS = [
    os.path.join(BASE_DIR, './indexing/Recipies/inverted_index.json'),
]
RECIPES_FOLDER_PATH = os.path.join(BASE_DIR, './indexing/Recipies/recipes')

# Mots vides (stop words) étendus
STOP_WORDS = {
    # Articles et mots courants
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 
    'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 
    'both', 'but', 'by', 'can', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'down', 
    'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having', 
    'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 
    'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 
    'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 
    'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 
    'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 
    'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 
    'who', 'whom', 'why', 'will', 'with', 'would', 'you', 'your', 'yours', 'yourself', 
    'yourselves',
    
    # Termes culinaires génériques
    'recipe', 'recipes', 'dish', 'dishes', 'cook', 'cooking', 'cooked', 'cuisine', 
    'food', 'ingredient', 'ingredients', 'preparation', 'prepare', 'prepared', 'preparing', 
    'step', 'steps', 'method', 'instructions', 'serves', 'serving', 'servings', 'make', 
    'makes', 'making', 'made', 'add', 'adding', 'added', 'adds', 'mix', 'mixing', 'mixed', 
    'place', 'placing', 'placed', 'put', 'putting', 'heat', 'heating', 'heated', 'boil', 
    'boiling', 'boiled', 'stir', 'stirring', 'stirred', 'pour', 'pouring', 'poured', 
    'remove', 'removing', 'removed', 'cut', 'cutting', 'cuts', 'chop', 'chopping', 
    'chopped', 'slice', 'slicing', 'sliced', 'bake', 'baking', 'baked', 'fry', 'frying', 
    'fried', 'simmer', 'simmering', 'simmered', 'season', 'seasoning', 'seasoned', 'taste', 
    'tasting', 'serve', 'served', 'let', 'allow', 'bring', 'take', 'use', 'using', 'used', 
    'set', 'get', 'become',
    
    # Unités de mesure et temps
    'minute', 'minutes', 'hour', 'hours', 'second', 'seconds', 'time', 'times', 'cup', 
    'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons', 'tbsp', 'tsp', 'ounce', 
    'ounces', 'oz', 'pound', 'pounds', 'lb', 'lbs', 'gram', 'grams', 'kilogram', 
    'kilograms', 'kg', 'liter', 'liters', 'milliliter', 'milliliters', 'ml', 'piece', 
    'pieces', 'pinch', 'dash', 'handful',
    
    # Nombres
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 
    'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'hundred', 'thousand', 
    'first', 'second', 'third', 'fourth', 'half', 'quarter',
    
    # Mots additionnels spécifiques
    'style', 'traditional', 'dried', 'fruits', 'seeds'
}


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def load_json_file(file_path):
    """Charge un fichier JSON avec gestion des erreurs"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return []
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {file_path}: {e}")
        return []


def load_recipes_data():
    """Charge les données des recettes depuis le fichier JSON principal"""
    return load_json_file(RECIPES_JSON_PATH)


def load_user_recipes():
    """Charge les recettes créées par les utilisateurs"""
    return load_json_file(USER_RECIPES_PATH)


def load_inverted_index():
    """Charge l'inverted index depuis le premier chemin disponible"""
    for path in INVERTED_INDEX_PATHS:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            print(f"🔍 Inverted index chargé depuis: {abs_path}")
            return load_json_file(abs_path)
    
    print("❌ Aucun fichier inverted_index.json trouvé")
    return {}


def normalize_keyword(keyword):
    """
    Normalise un mot-clé pour la recherche
    """
    # Convertir en minuscules et supprimer les espaces inutiles
    keyword = keyword.lower().strip()
    
    # Supprimer les caractères non alphabétiques
    keyword = re.sub(r'[^a-z\s]', ' ', keyword)
    
    # Retirer les accents
    keyword = ''.join(
        c for c in unicodedata.normalize('NFD', keyword)
        if unicodedata.category(c) != 'Mn' or c == ' '
    )
    
    # Filtrer les mots vides et les mots trop courts
    words = keyword.split()
    filtered_words = [w for w in words if len(w) > 2 and w not in STOP_WORDS]
    
    return ' '.join(filtered_words) if filtered_words else ''


def get_recipe_by_filename(filename):
    """
    Récupère une recette à partir de son fichier JSON
    """
    # Nettoyer et compléter le nom de fichier
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    
    file_path = os.path.join(RECIPES_FOLDER_PATH, filename)
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)
        
        # Log de débogage pour les images
        log_image_info(filename, recipe_data)
        
        # Ajouter l'ID de la recette
        recipe_data['id'] = filename.replace('.json', '')
        
        # Adapter le format aux attentes de l'API
        recipe_data = adapt_recipe_format(recipe_data)
        
        # Gérer l'URL de l'image (pour les recettes indexées)
        recipe_data = handle_recipe_image(recipe_data)
        
        log_recipe_info(recipe_data)
        
        return recipe_data
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture du fichier {filename}: {e}")
        traceback.print_exc()
        return None


def adapt_recipe_format(recipe_data):
    """Adapte le format de la recette au format attendu par l'API"""
    # Gérer le titre
    if 'name' in recipe_data and 'title' not in recipe_data:
        recipe_data['title'] = recipe_data['name']
    
    # Créer une description si absente
    if 'description' not in recipe_data or not recipe_data.get('description'):
        recipe_data['description'] = generate_recipe_description(recipe_data)
    
    # Assurer la présence des champs requis
    recipe_data.setdefault('ingredients', [])
    recipe_data.setdefault('steps', [])
    recipe_data.setdefault('author', {'name': 'Chef Traditionnel'})
    
    return recipe_data


def generate_recipe_description(recipe_data):
    """Génère une description pour une recette"""
    title = recipe_data.get('title') or recipe_data.get('name', 'Recette Marocaine')
    ingredients = recipe_data.get('ingredients', [])
    
    if isinstance(ingredients, list) and ingredients:
        main_ingredients = extract_main_ingredients(ingredients[:3])
        if main_ingredients:
            ing_text = ', '.join(main_ingredients)
            return f"{title} - Recette marocaine traditionnelle avec {ing_text}"
    
    return f"{title} - Recette marocaine traditionnelle"


def extract_main_ingredients(ingredients):
    """Extrait les ingrédients principaux d'une liste"""
    main_ingredients = []
    for ing in ingredients:
        clean_ing = re.sub(r'^[\d\s/.,]+[a-z]*\s*', '', ing, flags=re.IGNORECASE)
        clean_ing = clean_ing.split(',')[0].strip()
        if clean_ing and len(clean_ing) > 2:
            main_ingredients.append(clean_ing.lower())
    return main_ingredients


def handle_recipe_image(recipe_data):
    """Gère la conversion du chemin d'image en URL pour les recettes indexées"""
    if 'image' in recipe_data and recipe_data['image']:
        original_image = recipe_data['image']
        # Nettoyer le chemin pour ne garder que le nom de fichier (Ex: tajine_poulet.jpg)
        clean_filename = os.path.basename(original_image)
        # Construire l'URL publique : /media/tajine_poulet.jpg
        recipe_data['image'] = f"{settings.MEDIA_URL}{clean_filename}"
        print(f"🔄 Conversion image: {original_image} → {recipe_data['image']}")
    
    return recipe_data


def log_image_info(filename, recipe_data):
    """Journalise les informations sur l'image d'une recette"""
    image_present = 'image' in recipe_data
    print(f"    🖼️ [IMAGE LOG] Fichier: {filename}")
    print(f"    🖼️ [IMAGE LOG] Champ 'image' présent: {image_present}")
    if image_present:
        print(f"    🖼️ [IMAGE LOG] Valeur: {recipe_data['image']}")
        print(f"    🖼️ [IMAGE LOG] Type: {type(recipe_data['image'])}")


def log_recipe_info(recipe_data):
    """Journalise les informations d'une recette"""
    print(f"    ✅ Données adaptées:")
    print(f"      - Titre: {recipe_data.get('title')}")
    print(f"      - Description: {recipe_data.get('description', 'N/A')[:50]}...")
    print(f"      - Ingrédients: {len(recipe_data.get('ingredients', []))}")
    print(f"      - Étapes: {len(recipe_data.get('steps', []))}")


# ============================================================
# FONCTIONS DE RECHERCHE
# ============================================================

def search_recipes_by_analysis(nom_recette, ingredients_visibles, inverted_index):
    """
    Recherche des recettes avec pondération
    """
    print(f"\n🧠 Recherche pondérée: Nom='{nom_recette}', Ingrédients={ingredients_visibles}")
    
    recipe_scores = {}
    search_terms = build_search_terms(nom_recette, ingredients_visibles)
    
    # Rechercher chaque terme dans l'index
    for term, weight in search_terms:
        search_term_in_index(term, weight, inverted_index, recipe_scores)
    
    if not recipe_scores:
        print("❌ Aucune recette trouvée")
        return []
    
    # Trier et récupérer les meilleures recettes
    return get_top_recipes(recipe_scores)


def build_search_terms(nom_recette, ingredients_visibles):
    """Construit la liste des termes de recherche avec leurs poids"""
    search_terms = []
    
    # Poids élevé pour le nom de la recette
    if nom_recette:
        search_terms.append((nom_recette, 5.0))
    
    # Poids moyen pour les ingrédients
    for ing in ingredients_visibles:
        if ing.lower() != nom_recette.lower():
            search_terms.append((ing, 2.0))
    
    return search_terms


def search_term_in_index(term, weight, inverted_index, recipe_scores):
    """Recherche un terme dans l'index inversé"""
    term_normalized = normalize_keyword(term)
    
    if not term_normalized:
        return
    
    words_to_search = term_normalized.split()
    
    for word in words_to_search:
        if len(word) < 3:
            continue
        
        # Recherche exacte
        if word in inverted_index:
            add_score_to_recipes(inverted_index[word], weight, recipe_scores)
        # Recherche partielle (avec poids réduit)
        elif len(word) >= 4:
            search_partial_match(word, weight, inverted_index, recipe_scores)


def search_partial_match(word, weight, inverted_index, recipe_scores):
    """Recherche des correspondances partielles"""
    for index_key, recipe_files in inverted_index.items():
        if word in index_key or index_key in word:
            add_score_to_recipes(recipe_files, weight * 0.5, recipe_scores)


def add_score_to_recipes(recipe_files, score, recipe_scores):
    """Ajoute un score à une liste de recettes"""
    for recipe_file in recipe_files:
        if recipe_file not in recipe_scores:
            recipe_scores[recipe_file] = 0
        recipe_scores[recipe_file] += score


def get_top_recipes(recipe_scores, limit=5):
    """Récupère les meilleures recettes basées sur leur score"""
    sorted_recipe_ids = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"📊 Top {limit} fichiers trouvés: {sorted_recipe_ids[:limit]}")
    
    top_recipes = []
    for filename, score in sorted_recipe_ids[:limit]:
        recipe = get_recipe_by_filename(filename)
        if recipe:
            recipe['match_score'] = score
            top_recipes.append(recipe)
        else:
            print(f"⚠️ Fichier non trouvé: '{filename}' (Score: {score:.2f})")
    
    print(f"✅ Top {len(top_recipes)} recettes trouvées")
    return top_recipes


# ============================================================
# ENDPOINTS API
# ============================================================

@require_http_methods(["GET"])
def get_all_recipes(request):
    """Récupère toutes les recettes"""
    recipes_data = load_recipes_data()
    user_recipes = load_user_recipes()
    all_recipes = recipes_data + user_recipes
    return JsonResponse({'success': True, 'recipes': all_recipes})


@require_http_methods(["GET"])
def search_recipes(request):
    """Recherche des recettes par texte"""
    query = request.GET.get('query', '').lower().strip()
    
    if not query:
        return JsonResponse({'success': True, 'recipes': []})
    
    all_recipes = load_recipes_data() + load_user_recipes()
    
    results = [
        recipe for recipe in all_recipes 
        if (query in recipe.get('title', '').lower() or
            any(query in ingredient.lower() for ingredient in recipe.get('ingredients', [])))
    ]
    
    return JsonResponse({'success': True, 'recipes': results})


@require_http_methods(["GET"])
def get_recipe_details(request, recipe_id):
    """Récupère les détails d'une recette spécifique"""
    print(f"📥 Demande de détails pour: {recipe_id}")
    
    recipe_id = recipe_id.strip('/')
    
    # Chercher d'abord dans les fichiers JSON
    recipe = get_recipe_by_filename(recipe_id)
    
    # Sinon chercher dans les listes chargées
    if not recipe:
        all_recipes = load_recipes_data() + load_user_recipes()
        recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    
    # Gérer l'URL de l'image si la recette vient des listes chargées et n'a pas été traitée
    if recipe and 'image' in recipe and recipe['image'] and not recipe['image'].startswith(settings.MEDIA_URL):
        recipe = handle_recipe_image(recipe)

    if recipe:
        print(f"✅ Recette trouvée: {recipe.get('title', 'Sans titre')}")
        return JsonResponse({'success': True, 'recipe': recipe})
    else:
        print(f"❌ Recette non trouvée: {recipe_id}")
        return JsonResponse({'success': False, 'error': 'Recette non trouvée'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_recipe_image(request):
    """Analyse une image pour identifier une recette"""
    try:
        print("📸 Analyse d'image avec recherche pondérée")
        
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'Aucune image fournie'}, status=400)
        
        # Charger et analyser l'image
        image_file = request.FILES['image']
        analysis_result = analyze_image_with_gemini(image_file)
        
        if not analysis_result:
            return JsonResponse({'success': False, 'error': 'Erreur d\'analyse d\'image'}, status=500)
        
        # Rechercher les recettes correspondantes
        inverted_index = load_inverted_index()
        if not inverted_index:
            return JsonResponse({'success': False, 'error': 'Index non disponible'}, status=500)
        
        matching_recipes = search_recipes_by_analysis(
            analysis_result['nom_recette'],
            analysis_result['ingredients_visibles'],
            inverted_index
        )
        
        log_matching_recipes(matching_recipes)
        
        return JsonResponse({
            'success': True,
            'matching_recipes': matching_recipes,
            'count': len(matching_recipes)
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def analyze_image_with_gemini(image_file):
    """Analyse une image avec l'API Gemini"""
    try:
        image = Image.open(image_file)
    except Exception:
        return None
    
    # Assurez-vous que la clé API est définie dans votre environnement
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyALE1SZtmuISUME7XO90iCm9sDTV8ZFC4o") 
    client = genai.Client(api_key=api_key)
    
    prompt = """Analyse cette image de plat marocain et réponds UNIQUEMENT en JSON avec cette structure exacte:
{
  "nom_recette": "nom de base du plat (exemple: tagine, pastilla, couscous, harira, etc.)",
  "ingredients_visibles": ["ingredient1", "ingredient2", "ingredient3", ...]
}

IMPORTANT:
- "nom_recette" doit contenir UNIQUEMENT le nom de base du plat marocain
- Ne PAS inclure les ingrédients dans le nom
- Réponds UNIQUEMENT avec le JSON, sans texte additionnel"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, image],
        config=types.GenerateContentConfig(response_modalities=['TEXT'])
    )
    
    response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
    
    try:
        result = json.loads(response_text)
        return {
            'nom_recette': result.get('nom_recette', '').lower().strip(),
            'ingredients_visibles': [ing.lower().strip() for ing in result.get('ingredients_visibles', [])]
        }
    except json.JSONDecodeError:
        return None


def log_matching_recipes(matching_recipes):
    """Journalise les recettes correspondantes"""
    print(f"\n🖼️ [IMAGE LOG] Vérification des images dans {len(matching_recipes)} résultats:")
    for i, recipe in enumerate(matching_recipes, 1):
        print(f"  Recette {i}: {recipe.get('title', 'Sans titre')}")
        print(f"      🖼️ Champ 'image' présent: {'image' in recipe}")
        print(f"      🖼️ Valeur: {recipe.get('image', 'AUCUNE')}")


@csrf_exempt
@require_http_methods(["POST"])
def create_user_recipe(request):
    """Crée une nouvelle recette utilisateur"""
    try:
        # Récupérer les données du formulaire
        required_fields = ['title', 'description', 'ingredients', 'steps']
        field_values = {}
        
        for field in required_fields:
            value = request.POST.get(field, '').strip()
            if not value:
                return JsonResponse({'success': False, 'error': f'Le champ {field} est requis'}, status=400)
            field_values[field] = value
        
        user_name = request.POST.get('user_name', 'Chef zahira').strip()
        
        # Valider et parser les listes
        try:
            ingredients_list = json.loads(field_values['ingredients'])
            steps_list = json.loads(field_values['steps'])
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Format des ingrédients ou étapes invalide'}, status=400)
        
        # Gérer l'image téléchargée
        image_url = handle_uploaded_image(request) # <-- Appel à la fonction corrigée
        
        # Créer l'objet recette
        recipe_data = {
            'id': f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            'title': field_values['title'],
            'description': field_values['description'],
            'ingredients': ingredients_list,
            'steps': steps_list,
            'image': image_url, # <-- L'URL est maintenant correcte (/media/nom_du_fichier.jpg)
            'author': {'name': user_name},
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_created': True
        }
        
        # Sauvegarder la recette
        save_user_recipe(recipe_data)
        
        return JsonResponse({
            'success': True, 
            'recipe': recipe_data, 
            'message': 'Recette créée avec succès !'
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Impossible de créer la recette.'}, status=500)


def handle_uploaded_image(request):
    """
    CORRECTION APPLIQUÉE ICI: Gère le téléchargement d'une image en utilisant 
    settings.MEDIA_ROOT et settings.MEDIA_URL pour garantir que l'image est 
    sauvegardée au bon endroit et a une URL correcte.
    """
    if 'image' not in request.FILES:
        return None
    
    image_file = request.FILES['image']
    
    # 1. Utiliser le chemin physique MEDIA_ROOT pour le dossier d'upload
    # MEDIA_ROOT = '.../search_api/indexing/Recipies/images'
    upload_dir = settings.MEDIA_ROOT 
    os.makedirs(upload_dir, exist_ok=True)
    
    # 2. Générer un nom de fichier unique et sécurisé
    extension = os.path.splitext(image_file.name)[1]
    filename = f"{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(upload_dir, filename)
    
    # 3. Sauvegarde du fichier
    with open(filepath, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    
    # 4. Retourner l'URL publique (/media/nom_fichier_unique.ext)
    return f"{settings.MEDIA_URL}{filename}"


def save_user_recipe(recipe_data):
    """Sauvegarde une recette utilisateur dans le fichier JSON"""
    user_recipes = load_user_recipes()
    user_recipes.append(recipe_data)
    
    with open(USER_RECIPES_PATH, 'w', encoding='utf-8') as f:
        json.dump(user_recipes, f, ensure_ascii=False, indent=2)


@require_http_methods(["GET"])
def get_user_recipes(request):
    """Récupère toutes les recettes utilisateur"""
    user_recipes = load_user_recipes()
    return JsonResponse({'success': True, 'recipes': user_recipes})

@csrf_exempt
def voice_search(request):
    """
    Endpoint pour la recherche vocale avec transcription Gemini puis recherche
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    # Appeler la fonction transcribe
    transcription_response = transcribe(request)
    
    # Si erreur de transcription, retourner directement
    if transcription_response.status_code != 200:
        return transcription_response
    
    # Parser la réponse JSON de transcription
    transcription_data = json.loads(transcription_response.content)
    
    # Vérifier le succès
    if not transcription_data.get('success', False):
        return transcription_response
    
    # Récupérer le texte transcrit (priorité à la traduction si disponible)
    query = transcription_data.get('translation') or transcription_data.get('transcription', '')
    
    if not query or query.upper() == 'N/A':
        query = transcription_data.get('transcription', '')
    
    if not query:
        return JsonResponse({
            "error": "Aucune transcription obtenue",
            "success": False
        }, status=400)
    
    # Charger les recettes
    try:
        recipes_data = load_recipes_data()
    except Exception as e:
        return JsonResponse({
            'error': f'Erreur chargement recettes: {str(e)}',
            'success': False
        }, status=500)
    
    # Rechercher dans les recettes
    query_lower = query.lower().strip()
    results = []
    
    for recipe in recipes_data:
        title_match = query_lower in recipe.get('title', '').lower()
        description_match = query_lower in recipe.get('description', '').lower()
        ingredients_match = any(
            query_lower in str(ingredient).lower() 
            for ingredient in recipe.get('ingredients', [])
        )
        
        if title_match or description_match or ingredients_match:
            results.append(recipe)
    
    return JsonResponse({
        'success': True,
        'transcription': transcription_data.get('transcription', ''),
        'translation': transcription_data.get('translation'),
        'query': query,
        'results': results,
        'count': len(results),
        'model': transcription_data.get('model', 'unknown')
    })