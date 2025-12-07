"""
Views pour l'API de recherche de recettes marocaines avec Inverted Index
(Version finale avec correction du chemin d'accès aux fichiers et amélioration du filtrage des mots-clés)
"""

import json
import os
import time
import uuid
import traceback
import glob
import unicodedata
import re # Importation de re pour la normalisation

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from google import genai
from google.genai import types
from PIL import Image


# ============================================================
# CHARGEMENT DES DONNÉES ET UTILITAIRES
# ============================================================

def load_recipes_data():
    """Charge les données des recettes depuis le fichier JSON"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), '../data/recipes.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception:
        return []

def load_user_recipes():
    """Charge les recettes créées par les utilisateurs"""
    try:
        user_recipes_file = os.path.join(os.path.dirname(__file__), '../data/user_recipes.json')
        if os.path.exists(user_recipes_file):
            with open(user_recipes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception:
        return []

def load_inverted_index():
    """Charge l'inverted index."""
    try:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), './indexing/Recipies/inverted_index.json'),
        ]
        
        print("🔍 Recherche du fichier inverted_index.json...")
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"   ✅ Inverted index chargé: {len(data)} entrées")
                    return data
        
        print("❌ Fichier inverted_index.json introuvable.")
        return {}
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'inverted index: {e}")
        return {}


def normalize_keyword(keyword):
    """
    Normalise un mot-clé pour la recherche :
    1. Minuscule et suppression de la ponctuation/chiffres.
    2. Suppression des accents.
    3. Filtrage des mots vides étendus.
    """
    keyword = keyword.lower().strip()
    
    # 1. Suppression des caractères non alphabétiques (chiffres, ponctuation, etc.)
    keyword = re.sub(r'[^a-z\s]', ' ', keyword)
    
    # 2. Retirer les accents
    keyword = ''.join(
        c for c in unicodedata.normalize('NFD', keyword)
        if unicodedata.category(c) != 'Mn' or c == ' '
    )
    
    # 3. Mots Arrêt Améliorés (Stop Words en anglais)
    stop_words = {
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
        # Stop words spécifiques aux recettes
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
        # Temps et quantités
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
        # Mots additionnels
        'style', 'traditional', 'dried', 'fruits', 'seeds'
    }
    
    words = keyword.split()
    # Filtrer les mots vides et les mots très courts
    words = [w for w in words if len(w) > 2 and w not in stop_words]
    
    # Retourner la chaîne nettoyée
    return ' '.join(words) if words else ''


# ============================================================
# 🔑 FONCTION CLÉ : RÉCUPÉRATION PAR NOM DE FICHIER (CHEMIN CORRIGÉ)
# ============================================================

def get_recipe_by_filename(filename):
    """
    Récupère la recette détaillée en ouvrant le fichier JSON correspondant
    dans le dossier de l'indexation. (Correction du chemin d'accès).
    """
    # 🎯 Correction du chemin pour pointer vers le dossier ./indexing/Recipies
    recipes_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 
            './indexing/Recipies/recipes' 
        )
    )
    
    # Nettoyer le nom de fichier
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    
    file_path = os.path.join(recipes_folder, filename)

    if not os.path.exists(file_path):
        print(f"    ❌ Fichier non trouvé dans le chemin corrigé: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)
            
            print(f"    📄 Données brutes du fichier {filename}: {recipe_data}")
            
            # 🖼️ LOGS POUR LE CHAMP IMAGE - DÉBUT
            image_present = 'image' in recipe_data
            print(f"    🖼️ [IMAGE LOG] Champ 'image' présent dans le JSON: {image_present}")
            if image_present:
                image_val = recipe_data['image']
                print(f"    🖼️ [IMAGE LOG] Valeur: {image_val}")
                print(f"    🖼️ [IMAGE LOG] Type: {type(image_val)}")
            else:
                print(f"    ⚠️ [IMAGE LOG] ATTENTION: Champ 'image' ABSENT dans {filename}")
            # 🖼️ LOGS POUR LE CHAMP IMAGE - FIN
            
            # Ajout du nom du fichier comme ID
            recipe_data['id'] = filename.replace('.json', '')
            
            # ADAPTATION AU FORMAT DE VOTRE FICHIER JSON
            # Si le fichier a "name" au lieu de "title", on adapte
            if 'name' in recipe_data and 'title' not in recipe_data:
                recipe_data['title'] = recipe_data['name']
            
            # Si le fichier n'a pas de "description", on en crée une
            if 'description' not in recipe_data or not recipe_data.get('description'):
                title = recipe_data.get('title') or recipe_data.get('name', 'Recette Marocaine')
                ingredients = recipe_data.get('ingredients', [])
                
                if isinstance(ingredients, list) and len(ingredients) > 0:
                    main_ingredients = []
                    for ing in ingredients[:3]:
                        # Nettoyer l'ingrédient
                        clean_ing = re.sub(r'^[\d\s/.,]+[a-z]*\s*', '', ing, flags=re.IGNORECASE)
                        clean_ing = clean_ing.split(',')[0].strip()
                        if clean_ing and len(clean_ing) > 2:
                            main_ingredients.append(clean_ing.lower())
                    
                    if main_ingredients:
                        ing_text = ', '.join(main_ingredients)
                        recipe_data['description'] = f"{title} - Recette marocaine traditionnelle avec {ing_text}"
                    else:
                        recipe_data['description'] = f"{title} - Recette marocaine traditionnelle"
                else:
                    recipe_data['description'] = f"{title} - Recette marocaine traditionnelle"
            
            # S'assurer que toutes les clés requises existent
            if 'ingredients' not in recipe_data:
                recipe_data['ingredients'] = []


import json
import os
import time
import uuid
import traceback
import glob
import unicodedata
import re # Importation de re pour la normalisation

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from google import genai
from google.genai import types
from PIL import Image

# ============================================================
# CHARGEMENT DES DONNÉES ET UTILITAIRES
# ============================================================

def load_recipes_data():
    """Charge les données des recettes depuis le fichier JSON"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), '../data/recipes.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception:
        return []

def load_user_recipes():
    """Charge les recettes créées par les utilisateurs"""
    try:
        user_recipes_file = os.path.join(os.path.dirname(__file__), '../data/user_recipes.json')
        if os.path.exists(user_recipes_file):
            with open(user_recipes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception:
        return []

def load_inverted_index():
    """Charge l'inverted index."""
    try:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), './indexing/Recipies/inverted_index.json'),
        ]
        
        print("🔍 Recherche du fichier inverted_index.json...")
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"   ✅ Inverted index chargé: {len(data)} entrées")
                    return data
        
        print("❌ Fichier inverted_index.json introuvable.")
        return {}
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'inverted index: {e}")
        return {}

def normalize_keyword(keyword):
    """
    Normalise un mot-clé pour la recherche :
    1. Minuscule et suppression de la ponctuation/chiffres.
    2. Suppression des accents.
    3. Filtrage des mots vides étendus.
    """
    keyword = keyword.lower().strip()
    
    # 1. Suppression des caractères non alphabétiques (chiffres, ponctuation, etc.)
    keyword = re.sub(r'[^a-z\s]', ' ', keyword)
    
    # 2. Retirer les accents
    keyword = ''.join(
        c for c in unicodedata.normalize('NFD', keyword)
        if unicodedata.category(c) != 'Mn' or c == ' '
    )
    
    # 3. Mots Arrêt Améliorés (Stop Words en anglais)
    stop_words = {
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
        # Stop words spécifiques aux recettes
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
        # Temps et quantités
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
        # Mots additionnels
        'style', 'traditional', 'dried', 'fruits', 'seeds'
    }
    
    words = keyword.split()
    # Filtrer les mots vides et les mots très courts
    words = [w for w in words if len(w) > 2 and w not in stop_words]
    
    # Retourner la chaîne nettoyée
    return ' '.join(words) if words else ''

# ============================================================
# 🔑 FONCTION CLÉ : RÉCUPÉRATION PAR NOM DE FICHIER (CHEMIN CORRIGÉ)
# ============================================================

def get_recipe_by_filename(filename):
    """
    Récupère la recette détaillée en ouvrant le fichier JSON correspondant
    dans le dossier de l'indexation. (Correction du chemin d'accès).
    """
    # 🎯 Correction du chemin pour pointer vers le dossier ./indexing/Recipies
    recipes_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 
            './indexing/Recipies/recipes' 
        )
    )
    
    # Nettoyer le nom de fichier
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    
    file_path = os.path.join(recipes_folder, filename)

    if not os.path.exists(file_path):
        print(f"    ❌ Fichier non trouvé dans le chemin corrigé: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            recipe_data = json.load(f)
            
            print(f"    📄 Données brutes du fichier {filename}: {recipe_data}")
            
            # 🖼️ LOGS POUR LE CHAMP IMAGE - DÉBUT
            print(f"    🖼️ [IMAGE LOG] Champ 'image' présent dans le JSON: {'image' in recipe_data}")
            if 'image' in recipe_data:
                print(f"    🖼️ [IMAGE LOG] Valeur: {recipe_data['image']}")
                print(f"    🖼️ [IMAGE LOG] Type: {type(recipe_data['image'])}")
            else:
                print(f"    ⚠️ [IMAGE LOG] ATTENTION: Champ 'image' ABSENT dans {filename}")
            # 🖼️ LOGS POUR LE CHAMP IMAGE - FIN
            
            # Ajout du nom du fichier comme ID
            recipe_data['id'] = filename.replace('.json', '')
            
            # ADAPTATION AU FORMAT DE VOTRE FICHIER JSON
            # Si le fichier a "name" au lieu de "title", on adapte
            if 'name' in recipe_data and 'title' not in recipe_data:
                recipe_data['title'] = recipe_data['name']
            
            # Si le fichier n'a pas de "description", on en crée une
            if 'description' not in recipe_data or not recipe_data.get('description'):
                title = recipe_data.get('title') or recipe_data.get('name', 'Recette Marocaine')
                ingredients = recipe_data.get('ingredients', [])
                
                if isinstance(ingredients, list) and len(ingredients) > 0:
                    main_ingredients = []
                    for ing in ingredients[:3]:
                        # Nettoyer l'ingrédient
                        clean_ing = re.sub(r'^[\d\s/.,]+[a-z]*\s*', '', ing, flags=re.IGNORECASE)
                        clean_ing = clean_ing.split(',')[0].strip()
                        if clean_ing and len(clean_ing) > 2:
                            main_ingredients.append(clean_ing.lower())
                    
                    if main_ingredients:
                        ing_text = ', '.join(main_ingredients)
                        recipe_data['description'] = f"{title} - Recette marocaine traditionnelle avec {ing_text}"
                    else:
                        recipe_data['description'] = f"{title} - Recette marocaine traditionnelle"
                else:
                    recipe_data['description'] = f"{title} - Recette marocaine traditionnelle"
            
            # S'assurer que toutes les clés requises existent
            if 'ingredients' not in recipe_data:
                recipe_data['ingredients'] = []
            
            if 'steps' not in recipe_data:
                recipe_data['steps'] = []
            
            if 'author' not in recipe_data:
                recipe_data['author'] = {'name': 'Chef Traditionnel'}
            
            print(f"    ✅ Données adaptées pour {filename}:")
            print(f"       - Titre: {recipe_data.get('title')}")
            print(f"       - Description: {recipe_data.get('description', 'N/A')[:50]}...")
            print(f"       - Ingrédients: {len(recipe_data.get('ingredients', []))}")
            print(f"       - Étapes: {len(recipe_data.get('steps', []))}")
            
            # 🖼️ LOGS POUR LE CHAMP IMAGE APRÈS TRAITEMENT - DÉBUT
            print(f"       🖼️ [IMAGE LOG FINAL] Présent: {'image' in recipe_data}")
            image_value_final = recipe_data.get('image', 'AUCUNE IMAGE')
            print(f"       🖼️ [IMAGE LOG FINAL] Valeur: {image_value_final}")
            print(f"       🖼️ [IMAGE LOG FINAL] Est None: {recipe_data.get('image') is None}")
            print(f"       🖼️ [IMAGE LOG FINAL] Est vide: {recipe_data.get('image') == ''}")
            # 🖼️ LOGS POUR LE CHAMP IMAGE APRÈS TRAITEMENT - FIN
            
            return recipe_data
    except Exception as e:
        print(f"    ⚠️ Erreur lecture fichier {filename}: {e}")
        traceback.print_exc()
        return None

# ============================================================
# FONCTION: RECHERCHE PONDÉRÉE PAR ANALYSE GEMINI (MISE À JOUR)
# ============================================================

def search_recipes_by_analysis(nom_recette, ingredients_visibles, inverted_index):
    """
    Recherche les recettes dans l'inverted index avec une pondération.
    - Poids élevé pour le 'nom_recette'.
    - Poids moyen pour les 'ingredients_visibles'.
    Récupère directement les données en utilisant le nom du fichier.
    """
    print(f"\n🧠 Recherche pondérée: Nom='{nom_recette}', Ingrédients={ingredients_visibles}")
    
    recipe_scores = {}
    search_terms = []
    
    # Poids pour le Nom de la Recette (Haute importance)
    if nom_recette:
        search_terms.append({'term': nom_recette, 'weight': 5.0})

    # Poids pour les Ingrédients Visibles (Importance moyenne)
    for ing in ingredients_visibles:
        # On évite de dupliquer la recherche si le nom de recette est un ingrédient
        if ing.lower() != nom_recette.lower():
            search_terms.append({'term': ing, 'weight': 2.0})
            
    for item in search_terms:
        term = item['term']
        weight = item['weight']
        term_normalized = normalize_keyword(term)
        
        if not term_normalized:
            continue
            
        words_to_search = term_normalized.split()
        
        for word in words_to_search:
            if len(word) < 3:
                continue
                
            match_found = False
            
            # 1. Recherche exacte
            if word in inverted_index:
                recipe_files = inverted_index[word]
                match_found = True
                
                for recipe_file in recipe_files:
                    if recipe_file not in recipe_scores:
                        recipe_scores[recipe_file] = 0
                    # Ajout du poids exact
                    recipe_scores[recipe_file] += weight 
            
            # 2. Recherche partielle (avec un poids réduit)
            if not match_found and len(word) >= 4:
                for index_key, recipe_files in inverted_index.items():
                    # Utilise une recherche plus stricte pour le partiel pour éviter trop de bruit
                    if (word in index_key) or (index_key in word):
                        match_found = True
                        
                        for recipe_file in recipe_files:
                            if recipe_file not in recipe_scores:
                                recipe_scores[recipe_file] = 0
                            # Ajout du poids réduit pour le partiel (ex: 50% du poids original)
                            recipe_scores[recipe_file] += (weight * 0.5) 
            
            if not match_found:
                print(f"    ❌ Aucune correspondance pour '{word}'")

    if not recipe_scores:
        print("   ❌ Aucune recette trouvée dans l'index après recherche pondérée")
        return []
        
    # Tri par score décroissant
    sorted_recipe_ids = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"📊 Top 5 Fichiers trouvés (à rechercher) : {sorted_recipe_ids[:5]}")
    
    top_recipes = []
    # On limite la récupération des détails aux 5 meilleures recettes
    for filename, score in sorted_recipe_ids[:5]:
        # RÉCUPÉRATION DIRECTE du fichier JSON
        recipe = get_recipe_by_filename(filename)
        
        if recipe:
            recipe_with_score = recipe.copy()
            recipe_with_score['match_score'] = score
            top_recipes.append(recipe_with_score)
        else:
            print(f"⚠️ FICHIER NON TROUVÉ : '{filename}' (Score: {score:.2f}). Vérifiez que le fichier existe bien dans le dossier Recipies.")
            
    print(f"   ✅ Top {len(top_recipes)} recettes trouvées.")
    return top_recipes

# ============================================================
# ENDPOINTS (Simplifiés pour clarté)
# ============================================================

@require_http_methods(["GET"])
def get_all_recipes(request):
    recipes_data = load_recipes_data()
    user_recipes = load_user_recipes()
    all_recipes = recipes_data + user_recipes
    return JsonResponse({'success': True, 'recipes': all_recipes})

@require_http_methods(["GET"])
def search_recipes(request):
    query = request.GET.get('query', '').lower().strip()
    all_recipes = load_recipes_data() + load_user_recipes()
    
    if not query:
        return JsonResponse({'success': True, 'recipes': []})
    
    results = [
        recipe for recipe in all_recipes 
        if query in recipe.get('title', '').lower() 
        or any(query in ingredient.lower() for ingredient in recipe.get('ingredients', []))
    ]
    
    return JsonResponse({'success': True, 'recipes': results})

@require_http_methods(["GET"])
def get_recipe_details(request, recipe_id):
    print(f"📥 Demande de détails pour la recette: {recipe_id}")
    
    # Nettoyer l'ID (enlever les barres obliques)
    recipe_id = recipe_id.strip('/')
    
    # 🔧 CORRECTION : Essayer d'abord avec le système de fichiers (indexing/Recipies/recipes/)
    print(f"🔍 Recherche dans indexing/Recipies/recipes/ pour: {recipe_id}")
    recipe = get_recipe_by_filename(recipe_id)
    
    if not recipe:
        # Sinon, cherche dans la liste chargée (pour les recettes utilisateur)
        print(f"🔍 Recherche dans recipes.json et user_recipes.json...")
        all_recipes = load_recipes_data() + load_user_recipes()
        recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    
    if recipe:
        print(f"✅ Recette trouvée: {recipe.get('title', 'Sans titre')}")
        print(f"   - ID: {recipe.get('id')}")
        print(f"   - Ingrédients: {len(recipe.get('ingredients', []))}")
        print(f"   - Étapes: {len(recipe.get('steps', []))}")
        
        # 🖼️ LOGS POUR LE CHAMP IMAGE AVANT RETOUR - DÉBUT
        print(f"   🖼️ [IMAGE LOG ENDPOINT] Champ présent: {'image' in recipe}")
        image_value = recipe.get('image', 'PAS D IMAGE')
        print(f"   🖼️ [IMAGE LOG ENDPOINT] Valeur: {image_value}")
        print(f"   🖼️ [IMAGE LOG ENDPOINT] Type: {type(recipe.get('image'))}")
        # 🖼️ LOGS POUR LE CHAMP IMAGE AVANT RETOUR - FIN
        
        return JsonResponse({'success': True, 'recipe': recipe})
    else:
        print(f"❌ Recette non trouvée: {recipe_id}")
        print(f"   Chemins vérifiés:")
        print(f"   1. indexing/Recipies/recipes/{recipe_id}.json")
        print(f"   2. ../data/recipes.json")
        print(f"   3. ../data/user_recipes.json")
        return JsonResponse({'success': False, 'error': 'Recette non trouvée'}, status=404)

# ============================================================
# ANALYSE D'IMAGE AVEC GOOGLE GEMINI + INVERTED INDEX
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
def analyze_recipe_image(request):
    try:
        print("📸 Requête d'analyse d'image reçue (Recherche Inverted Index Pondérée)")
        
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'Aucune image fournie'}, status=400)
        
        image_file = request.FILES['image']
        
        try:
            image = Image.open(image_file)
        except Exception:
            return JsonResponse({'error': 'Erreur ouverture image'}, status=400)
        
        api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyALE1SZtmuISUME7XO90iCm9sDTV8ZFC4o")
        client = genai.Client(api_key=api_key)
        
        # 🎯 PROMPT AMÉLIORÉ : Séparer nom de base et ingrédients
        prompt = """Analyse cette image de plat marocain et réponds UNIQUEMENT en JSON avec cette structure exacte:

{
  "nom_recette": "nom de base du plat (exemple: tagine, pastilla, couscous, harira, etc. - UN SEUL MOT sans les ingrédients)",
  "ingredients_visibles": ["ingredient1", "ingredient2", "ingredient3", ...]
}

IMPORTANT:
- "nom_recette" doit contenir UNIQUEMENT le nom de base du plat marocain (tagine, couscous, pastilla, etc.)
- Ne PAS inclure les ingrédients dans le nom (exemple: écris "tagine" et NON "tagine de poulet")
- "ingredients_visibles" doit contenir TOUS les ingrédients identifiables dans l'image
- Réponds UNIQUEMENT avec le JSON, sans texte additionnel"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image],
            config=types.GenerateContentConfig(response_modalities=['TEXT'])
        )
        
        response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        try:
            analysis_result = json.loads(response_text)
            nom_recette = analysis_result.get('nom_recette', '').lower().strip()
            ingredients_visibles = [ing.lower().strip() for ing in analysis_result.get('ingredients_visibles', [])]
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Format de réponse invalide de Gemini'}, status=500)
        
        inverted_index = load_inverted_index()
        
        if not inverted_index:
            return JsonResponse({'success': False, 'error': 'Problème de chargement de l\'index.'}, status=500)
        
        matching_recipes = search_recipes_by_analysis(
            nom_recette, 
            ingredients_visibles, 
            inverted_index
        )
        
        # 🖼️ LOGS POUR LES IMAGES DANS LES RÉSULTATS - DÉBUT
        print(f"\n🖼️ [IMAGE LOG RESULTS] Vérification des images dans {len(matching_recipes)} résultats:")
        for i, recipe in enumerate(matching_recipes, 1):
            recipe_title = recipe.get('title', 'Sans titre')
            print(f"   Recette {i}: {recipe_title}")
            print(f"       🖼️ Champ 'image' présent: {'image' in recipe}")
            recipe_image = recipe.get('image', 'AUCUNE')
            print(f"       🖼️ Valeur: {recipe_image}")
            print(f"       🖼️ Est None: {recipe.get('image') is None}")
            print(f"       🖼️ Est vide: {recipe.get('image') == ''}")
        # 🖼️ LOGS POUR LES IMAGES DANS LES RÉSULTATS - FIN
        
        # Retourner uniquement les recettes trouvées
        return JsonResponse({
            'success': True,
            'matching_recipes': matching_recipes,
            'count': len(matching_recipes)
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ============================================================
# CRÉATION DE RECETTES (Non modifiée)
# ============================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_user_recipe(request):
    try:
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        ingredients = request.POST.get('ingredients', '')
        steps = request.POST.get('steps', '')
        user_name = request.POST.get('user_name', 'Chef Anonyme').strip()
        
        if not all([title, description, ingredients, steps]):
            return JsonResponse({'success': False, 'error': 'Tous les champs sont requis'}, status=400)
        
        try:
            ingredients_list = json.loads(ingredients)
            steps_list = json.loads(steps)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Format des ingrédients ou étapes invalide'}, status=400)
        
        image_url = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            upload_dir = os.path.join(os.path.dirname(__file__), '../media/user_recipes')
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"{uuid.uuid4()}_{image_file.name}"
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            image_url = f"/media/user_recipes/{filename}"
        
        recipe_data = {
            'id': f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            'title': title,
            'description': description,
            'ingredients': ingredients_list,
            'steps': steps_list,
            'image': image_url,
            'author': {'name': user_name},
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_created': True
        }
        
        user_recipes_file = os.path.join(os.path.dirname(__file__), '../data/user_recipes.json')
        user_recipes = load_user_recipes()
        user_recipes.append(recipe_data)
        
        with open(user_recipes_file, 'w', encoding='utf-8') as f:
            json.dump(user_recipes, f, ensure_ascii=False, indent=2)
        
        return JsonResponse({'success': True, 'recipe': recipe_data, 'message': 'Recette créée avec succès !'})
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': 'Impossible de créer la recette.'}, status=500)

@require_http_methods(["GET"])
def get_user_recipes(request):
    user_recipes = load_user_recipes()
    return JsonResponse({'success': True, 'recipes': user_recipes})

