"""
Views pour l'API de recherche de recettes marocaines avec Inverted Index
(Version corrigée - API Gemini unifiée)
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

# Import pour charger les variables d'environnement
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# ============================================================
# CONSTANTES ET CONFIGURATION
# ============================================================

# Chemins des fichiers
BASE_DIR = os.path.dirname(__file__) 
RECIPES_JSON_PATH = os.path.join(BASE_DIR, '../data/recipes.json')
USER_RECIPES_PATH = os.path.join(BASE_DIR, '../data/user_recipes.json')
INVERTED_INDEX_PATHS = [
    os.path.join(BASE_DIR, './indexing/Recipies/inverted_index.json'),
]
RECIPES_FOLDER_PATH = os.path.join(BASE_DIR, './indexing/Recipies/recipes')

# Configuration Gemini (à faire une seule fois au démarrage)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ ERREUR: GEMINI_API_KEY non trouvée dans les variables d'environnement. "
                     "Veuillez la définir dans le fichier .env")
genai.configure(api_key=GEMINI_API_KEY)

# Mots vides (stop words) étendus
STOP_WORDS = {
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
    'minute', 'minutes', 'hour', 'hours', 'second', 'seconds', 'time', 'times', 'cup', 
    'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons', 'tbsp', 'tsp', 'ounce', 
    'ounces', 'oz', 'pound', 'pounds', 'lb', 'lbs', 'gram', 'grams', 'kilogram', 
    'kilograms', 'kg', 'liter', 'liters', 'milliliter', 'milliliters', 'ml', 'piece', 
    'pieces', 'pinch', 'dash', 'handful',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 
    'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'hundred', 'thousand', 
    'first', 'second', 'third', 'fourth', 'half', 'quarter',
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
    """Normalise un mot-clé pour la recherche"""
    keyword = keyword.lower().strip()
    keyword = re.sub(r'[^a-z\s]', ' ', keyword)
    keyword = ''.join(
        c for c in unicodedata.normalize('NFD', keyword)
        if unicodedata.category(c) != 'Mn' or c == ' '
    )
    
    words = keyword.split()
    filtered_words = [w for w in words if len(w) > 2 and w not in STOP_WORDS]
    
    return ' '.join(filtered_words) if filtered_words else ''


def get_recipe_by_filename(filename):
    """Récupère une recette à partir de son fichier JSON"""
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    
    file_path = os.path.join(RECIPES_FOLDER_PATH, filename)
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)
        
        log_image_info(filename, recipe_data)
        recipe_data['id'] = filename.replace('.json', '')
        recipe_data = adapt_recipe_format(recipe_data)
        recipe_data = handle_recipe_image(recipe_data)
        log_recipe_info(recipe_data)
        
        return recipe_data
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture du fichier {filename}: {e}")
        traceback.print_exc()
        return None


def adapt_recipe_format(recipe_data):
    """Adapte le format de la recette au format attendu par l'API"""
    if 'name' in recipe_data and 'title' not in recipe_data:
        recipe_data['title'] = recipe_data['name']
    
    if 'description' not in recipe_data or not recipe_data.get('description'):
        recipe_data['description'] = generate_recipe_description(recipe_data)
    
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
        clean_filename = os.path.basename(original_image)
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
    """Recherche des recettes avec pondération"""
    print(f"\n🧠 Recherche pondérée: Nom='{nom_recette}', Ingrédients={ingredients_visibles}")
    
    recipe_scores = {}
    search_terms = build_search_terms(nom_recette, ingredients_visibles)
    
    for term, weight in search_terms:
        search_term_in_index(term, weight, inverted_index, recipe_scores)
    
    if not recipe_scores:
        print("❌ Aucune recette trouvée")
        return []
    
    return get_top_recipes(recipe_scores)


def build_search_terms(nom_recette, ingredients_visibles):
    """Construit la liste des termes de recherche avec leurs poids"""
    search_terms = []
    
    if nom_recette:
        search_terms.append((nom_recette, 5.0))
    
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
        
        if word in inverted_index:
            add_score_to_recipes(inverted_index[word], weight, recipe_scores)
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
    recipe = get_recipe_by_filename(recipe_id)
    
    if not recipe:
        all_recipes = load_recipes_data() + load_user_recipes()
        recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    
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
        
        image_file = request.FILES['image']
        analysis_result = analyze_image_with_gemini(image_file)
        
        if not analysis_result:
            return JsonResponse({'success': False, 'error': 'Erreur d\'analyse d\'image'}, status=500)
        
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
    
    prompt = """Analyse cette image de plat marocain et réponds UNIQUEMENT en JSON avec cette structure exacte:
{
  "nom_recette": "nom de base du plat (exemple: tagine, pastilla, couscous, harira, etc.)",
  "ingredients_visibles": ["ingredient1", "ingredient2", "ingredient3", ...]
}

IMPORTANT:
- "nom_recette" doit contenir UNIQUEMENT le nom de base du plat marocain
- Ne PAS inclure les ingrédients dans le nom
- Réponds UNIQUEMENT avec le JSON, sans texte additionnel"""
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, image])
        response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        result = json.loads(response_text)
        return {
            'nom_recette': result.get('nom_recette', '').lower().strip(),
            'ingredients_visibles': [ing.lower().strip() for ing in result.get('ingredients_visibles', [])]
        }
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
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
        required_fields = ['title', 'description', 'ingredients', 'steps']
        field_values = {}
        
        for field in required_fields:
            value = request.POST.get(field, '').strip()
            if not value:
                return JsonResponse({'success': False, 'error': f'Le champ {field} est requis'}, status=400)
            field_values[field] = value
        
        user_name = request.POST.get('user_name', 'Chef zahira').strip()
        
        try:
            ingredients_list = json.loads(field_values['ingredients'])
            steps_list = json.loads(field_values['steps'])
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Format des ingrédients ou étapes invalide'}, status=400)
        
        image_url = handle_uploaded_image(request)
        
        recipe_data = {
            'id': f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            'title': field_values['title'],
            'description': field_values['description'],
            'ingredients': ingredients_list,
            'steps': steps_list,
            'image': image_url,
            'author': {'name': user_name},
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_created': True
        }
        
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
    """Gère le téléchargement d'une image"""
    if 'image' not in request.FILES:
        return None
    
    image_file = request.FILES['image']
    upload_dir = settings.MEDIA_ROOT 
    os.makedirs(upload_dir, exist_ok=True)
    
    extension = os.path.splitext(image_file.name)[1]
    filename = f"{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(upload_dir, filename)
    
    with open(filepath, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    
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
    """Endpoint pour la recherche vocale"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    transcription_response = transcribe(request)
    
    if transcription_response.status_code != 200:
        return transcription_response
    
    transcription_data = json.loads(transcription_response.content)
    
    if not transcription_data.get('success', False):
        return transcription_response
    
    query = transcription_data.get('translation') or transcription_data.get('transcription', '')
    
    if not query or query.upper() == 'N/A':
        query = transcription_data.get('transcription', '')
    
    if not query:
        return JsonResponse({
            "error": "Aucune transcription obtenue",
            "success": False
        }, status=400)
    
    inverted_index = load_inverted_index()
    if not inverted_index:
        return JsonResponse({
            'success': False,
            'error': 'Index non disponible',
            'query': query
        }, status=500)
    
    print(f"🗣️ Recherche vocale avec inverted index: '{query}'")
    
    analysis_result = analyze_text_query(query)
    
    matching_recipes = search_recipes_by_analysis(
        analysis_result['nom_recette'],
        analysis_result['ingredients_visibles'],
        inverted_index
    )
    
    log_matching_recipes(matching_recipes)
    
    return JsonResponse({
        'success': True,
        'transcription': transcription_data.get('transcription', ''),
        'translation': transcription_data.get('translation'),
        'query': query,
        'analysis_result': analysis_result,
        'matching_recipes': matching_recipes,
        'count': len(matching_recipes),
        'model': transcription_data.get('model', 'unknown')
    })


def analyze_text_query(query_text):
    """Analyse une requête texte pour extraire nom de recette et ingrédients"""
    query_lower = query_text.lower().strip()
    
    moroccan_dishes = {
        'tagine', 'tajine', 'couscous', 'pastilla', 'harira', 'rfissa', 'taktouka',
        'zaalouk', 'briouat', 'msemen', 'baghrir', 'shebakia', 'makouda',
        'kefta', 'merguez', 'tanjia', 'mrouzia', 'bastilla', 'bessara',
        'seffa', 'harcha', 'makrout', 'ghriba'
    }
    
    detected_dish = None
    for dish in moroccan_dishes:
        if dish in query_lower:
            detected_dish = dish
            break
    
    common_ingredients = {
        'poulet', 'chicken', 'agneau', 'lamb', 'boeuf', 'beef', 'poisson', 'fish',
        'légumes', 'vegetables', 'carottes', 'carrots', 'pommes de terre', 'potatoes',
        'oignons', 'onions', 'ail', 'garlic', 'citron', 'lemon', 'olives', 'olives',
        'amandes', 'almonds', 'noix', 'walnuts', 'raisins', 'raisins', 'pruneaux', 'prunes',
        'abricots', 'apricots', 'figues', 'figs', 'dattes', 'dates', 'miel', 'honey',
        'cannelle', 'cinnamon', 'gingembre', 'ginger', 'curcuma', 'turmeric',
        'cumin', 'cumin', 'paprika', 'paprika', 'safran', 'saffron', 'coriandre', 'coriander',
        'persil', 'parsley', 'menthe', 'mint', 'semoule', 'semolina', 'farine', 'flour',
        'oeufs', 'eggs', 'beurre', 'butter', 'huile', 'oil', 'sel', 'salt', 'poivre', 'pepper'
    }
    
    detected_ingredients = []
    words = query_lower.split()
    
    for word in words:
        clean_word = re.sub(r'[^a-zéèêëàâäôöûüç]', '', word)
        if clean_word in common_ingredients:
            detected_ingredients.append(clean_word)
    
    if not detected_ingredients:
        meaningful_words = [w for w in words if len(w) > 3 and w not in STOP_WORDS]
        if meaningful_words:
            detected_ingredients = meaningful_words[:3]
    
    return {
        'nom_recette': detected_dish or 'plat marocain',
        'ingredients_visibles': detected_ingredients[:5]
    }


@csrf_exempt
@require_http_methods(["POST"])
def text_search(request):
    """Endpoint pour la recherche textuelle Darija avec Gemini"""
    print("\n" + "="*80)
    print("🚀 DÉBUT RECHERCHE TEXTUELLE DARIJA")
    print("="*80)
    
    try:
        print(f"📥 MÉTHODE HTTP: {request.method}")
        print(f"📥 CONTENT-TYPE: {request.content_type}")
        
        try:
            raw_body = request.body.decode('utf-8')
            print(f"📥 CORPS BRUT REÇU ({len(raw_body)} caractères):")
            print(f"   '{raw_body[:200]}{'...' if len(raw_body) > 200 else ''}'")
            
            body = json.loads(raw_body)
            text = body.get("text", "").strip()
            
            print(f"\n📝 TEXTE DARIJA EXTRACT:")
            print(f"   '{text}'")
            print(f"   Longueur: {len(text)} caractères")
            
        except json.JSONDecodeError as json_err:
            print(f"❌ ERREUR JSON: {json_err}")
            return JsonResponse({
                'error': 'Format JSON invalide',
                'success': False,
                'details': str(json_err)
            }, status=400)
        except UnicodeDecodeError as unicode_err:
            print(f"❌ ERREUR UNICODE: {unicode_err}")
            return JsonResponse({
                'error': 'Erreur d\'encodage du texte',
                'success': False,
                'details': str(unicode_err)
            }, status=400)
        
        if not text:
            print("❌ ERREUR: Texte vide ou non fourni")
            return JsonResponse({
                "error": "Aucun texte fourni",
                "success": False
            }, status=400)
        
        print(f"\n🔑 VÉRIFICATION CLÉ API GEMINI")
        if not GEMINI_API_KEY or GEMINI_API_KEY == "":
            print("❌ ERREUR: Clé API Gemini non configurée")
            return JsonResponse({
                'success': False,
                'error': 'Configuration API manquante',
                'details': 'GEMINI_API_KEY non configurée'
            }, status=500)
        
        print(f"✅ Clé API configurée (longueur: {len(GEMINI_API_KEY)})")
        
        print(f"\n🤖 ANALYSE AVEC GEMINI")
        print(f"   Texte à analyser: '{text[:50]}...'")
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""This is Moroccan Darija written with French characters. Translate the text to English, but **do NOT translate any food names**. Keep the food names exactly as they appear. Translate all verbs, pronouns, and other words to English. Answer with the full translated sentence, keeping the food names intact. 

Text: "{text}"

Answer:"""
            
            print(f"📤 Envoi prompt à Gemini...")
            
            response = model.generate_content(prompt)
            dish_name_en = response.text.strip().lower()
            
            print(f"📥 Réponse Gemini brute: '{dish_name_en}'")
            
            dish_name_en = re.sub(r'[^\w\s]', '', dish_name_en)
            dish_name_en = dish_name_en.strip()
            
            print(f"✅ NOM DE PLAT NETTOYÉ: '{dish_name_en}'")
            
            if not dish_name_en or dish_name_en in ['', 'n/a', 'none', 'unknown']:
                print("❌ ERREUR: Nom de plat vide ou invalide")
                return JsonResponse({
                    'success': False,
                    'error': 'Impossible d\'extraire le nom du plat',
                    'text': text,
                    'details': 'Réponse Gemini invalide ou vide'
                }, status=500)
                
        except Exception as gemini_err:
            print(f"❌ ERREUR GEMINI: {gemini_err}")
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': 'Erreur lors de l\'analyse Gemini',
                'text': text,
                'details': str(gemini_err)
            }, status=500)
        
        print(f"\n📚 CHARGEMENT INDEX INVERSE")
        inverted_index = load_inverted_index()
        
        if not inverted_index:
            print("❌ ERREUR: Index inversé non disponible")
            return JsonResponse({
                'success': False,
                'error': 'Index non disponible',
                'text': text,
                'dish_name': dish_name_en
            }, status=500)
        
        print(f"✅ INDEX CHARGÉ: {len(inverted_index)} termes")
        
        print(f"\n🔍 RECHERCHE DANS L'INDEX")
        print(f"   Terme recherché: '{dish_name_en}'")
        
        recipe_scores = {}
        search_terms = [(dish_name_en, 5.0)]
        
        for term, weight in search_terms:
            term_normalized = normalize_keyword(term)
            print(f"   Terme normalisé: '{term_normalized}'")
            
            if term_normalized:
                words_to_search = term_normalized.split()
                for word in words_to_search:
                    if len(word) < 3:
                        continue
                    
                    if word in inverted_index:
                        print(f"   ✅ Mot '{word}' trouvé dans l'index")
                        for recipe_file in inverted_index[word]:
                            if recipe_file not in recipe_scores:
                                recipe_scores[recipe_file] = 0
                            recipe_scores[recipe_file] += weight
                    elif len(word) >= 4:
                        print(f"   🔍 Recherche partielle pour '{word}'")
        
        print(f"\n📊 RÉSULTATS RECHERCHE")
        if recipe_scores:
            sorted_recipe_ids = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)
            print(f"✅ {len(sorted_recipe_ids)} fichiers trouvés")
        else:
            print("❌ Aucun résultat trouvé")
            return JsonResponse({
                'success': True,
                'message': 'Aucune recette trouvée',
                'original_text': text,
                'dish_name_english': dish_name_en,
                'matching_recipes': [],
                'count': 0
            })
        
        print(f"\n📥 CHARGEMENT DES RECETTES")
        matching_recipes = []
        for filename, score in sorted_recipe_ids[:5]:
            recipe = get_recipe_by_filename(filename)
            if recipe:
                recipe['match_score'] = score
                matching_recipes.append(recipe)
                print(f"   ✅ '{filename}' chargé - Score: {score:.2f}")
            else:
                print(f"   ❌ '{filename}' NON TROUVÉ")
        
        print(f"\n✅ RECHERCHE TERMINÉE")
        print(f"   Recettes trouvées: {len(matching_recipes)}")
        print("="*80)
        
        return JsonResponse({
            'success': True,
            'message': 'Recherche Darija réussie',
            'original_text': text,
            'dish_name_english': dish_name_en,
            'matching_recipes': matching_recipes,
            'count': len(matching_recipes)
        })
        
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur: {str(e)}',
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)