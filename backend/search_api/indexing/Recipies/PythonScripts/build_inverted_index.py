import json
import os
import re
from typing import Dict, List, Set, Tuple

class StrictRecipeIndexer:
    def __init__(self):
        # --- LISTES (Identiques à la version anglaise précédente) ---
        self.valid_ingredients = {
            'chicken', 'lamb', 'beef', 'meat', 'fish', 'tuna', 'shrimp', 'prawn', 'veal', 
            'turkey', 'calamari', 'sardine', 'liver', 'brain', 'tripe', 'mutton', 'head', 'feet', 'khlii',
            'onion', 'garlic', 'tomato', 'potato', 'carrot', 'zucchini', 'olive', 'aubergine',
            'pepper', 'chili', 'prune', 'lemon', 'orange', 'raisin', 'almond', 'date',
            'mint', 'parsley', 'cilantro', 'ginger', 'cumin', 'paprika', 'turmeric', 'saffron', 
            'cinnamon', 'harissa', 'ras-el-hanout', 'anise', 'fennel',
            'couscous', 'semolina', 'fava', 'chickpea', 'lentil', 'rice', 'flour', 'wheat', 'barley',
            'bread', 'yeast', 'egg', 'cheese', 'butter', 'oil', 'smen', 'broth', 'stock', 'honey', 
            'sugar', 'milk', 'cream', 'coco', 'vinegar', 'pickle', 'merguez', 'kefta', 'dates'
        }
        self.main_dishes = {
            'tajine', 'tagine', 'couscous', 'pastilla', 'harira', 'briouate', 
            'rfissa', 'tangia', 'kefta', 'zaalouk', 'msemen', 'chebakia', 
            'bissara', 'mechoui', 'sellou', 'mint_tea', 'batbout', 'khobz', 
            'harcha', 'baghrir', 'rghaif', 'mlaoui', 'seffa', 'mrouzia', 
            'chorba', 'loubia', 'taktouka', 'salad', 'fekkas', 'ghriba', 
            'kaab_ghzal', 'makrout', 'halwa', 'soup', 'chermoula'
        }
        self.singular_map = {
            'tomatoes': 'tomato', 'potatoes': 'potato', 'olives': 'olive', 
            'eggs': 'egg', 'chickpeas': 'chickpea', 'lentils': 'lentil', 
            'prunes': 'prune', 'raisins': 'raisin', 'almonds': 'almond',
            'sardines': 'sardine', 'dates': 'date', 'shrimps': 'shrimp', 
            'favas': 'fava'
        }

    # --- MÉTHODES D'EXTRACTION (Identiques) ---
    def normalize_word(self, word: str) -> str:
        word = word.lower().strip()
        word = re.sub(r'[^a-z0-9\s-]', '', word)
        if word in self.singular_map:
            return self.singular_map[word]
        if word.endswith('s') and len(word) > 3:
            root_word = word[:-1] 
            if root_word in self.valid_ingredients.union(self.main_dishes):
                return root_word
        return word

    def extract_valid_ingredients(self, text: str) -> Set[str]:
        found = set()
        stop_words_local = {'moroccan', 'morocco', 'cups', 'spoons', 'tsp', 'tbsp', 'kg', 'g', 'oz', 'of', 'and', 'the', 'in', 'to', 'for', 'with'}
        words = re.sub(r'[^a-z0-9\s-]', ' ', text.lower()).split()
        for w in words:
            if w in stop_words_local:
                continue
            clean_w = self.normalize_word(w)
            if clean_w in self.valid_ingredients:
                found.add(clean_w)
        return found
        
    def extract_main_dishes_and_modifiers(self, recipe_name: str) -> Tuple[Set[str], Set[str]]:
        found_dishes = set()
        found_modifiers = set()
        words = re.sub(r'[^a-z0-9\s-]', ' ', recipe_name.lower()).split()
        stop_words_title = {'moroccan', 'style', 'traditional', 'and', 'with', 'in', 'of', 'a', 'the', 'at'}
        for w in words:
            if w in stop_words_title:
                continue
            clean_w = self.normalize_word(w)
            if clean_w in self.main_dishes:
                found_dishes.add(clean_w)
            elif clean_w in self.valid_ingredients:
                found_modifiers.add(clean_w)
        return found_dishes, found_modifiers

    # --- MÉTHODE PRINCIPALE DE CONSTRUCTION ---
    def build_index(self, directory: str) -> Dict[str, List[str]]:
        """Construit l'index inversé fusionné."""
        final_index = {} # Utilisé pour fusionner ingrédient_index et dish_index
        
        if not os.path.exists(directory):
            print(f"❌ Erreur: Dossier '{directory}' introuvable.")
            return {}

        files = [f for f in os.listdir(directory) if f.endswith('.json')]
        # Le script va maintenant traiter TOUS les fichiers JSON trouvés.
        print(f"Traiter {len(files)} recettes...") 

        for filename in files:
            path = os.path.join(directory, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                recipe_name = data.get('name', '')
                ingredients_list = data.get('ingredients', [])
                
                full_text_ingredients = " ".join(ingredients_list)
                found_ingredients = self.extract_valid_ingredients(full_text_ingredients)
                found_dishes, found_modifiers = self.extract_main_dishes_and_modifiers(recipe_name)
                
                # Fusion des termes à indexer pour cette recette
                terms_to_index = found_ingredients.union(found_modifiers).union(found_dishes)
                
                # Mise à jour de l'index principal
                for term in terms_to_index:
                    if term not in final_index:
                        final_index[term] = []
                    # S'assurer que le nom du fichier est ajouté une seule fois
                    if filename not in final_index[term]:
                         final_index[term].append(filename) 
                    
            except Exception as e:
                print(f"⚠️ Erreur sur {filename}: {e}")
        
        # Tri et Finalisation
        sorted_index = {}
        for k in sorted(final_index.keys()):
            sorted_index[k] = sorted(final_index[k])
            
        return sorted_index

# --- LANCEMENT ---
if __name__ == "__main__":
    RECIPES_DIR = "C:/Users/j\Desktop/📦 smart-moroccan-cuisine/backend/search_api/indexing/Recipies/recipes"
    OUTPUT_FILE = "inverted_index_final.json"
    
    indexer = StrictRecipeIndexer()
    final_index = indexer.build_index(RECIPES_DIR)
    
    if final_index:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_index, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Index inversé généré avec succès dans '{OUTPUT_FILE}'")
        print(f"Nombre de termes indexés : {len(final_index)}")
        
        # Test de l'indexation par plat (tagine) et par ingrédient (chicken)
        print("\n--- TEST DE L'INDEXATION CORRIGÉE ---")
        
        tagine_key = 'tagine'
        if tagine_key in final_index:
            print(f"🍽️ {tagine_key} (Type de Plat) trouvé dans {len(final_index[tagine_key])} recettes.")

        chicken_key = 'chicken'
        if chicken_key in final_index:
            print(f"🐔 {chicken_key} (Ingrédient) trouvé dans {len(final_index[chicken_key])} recettes.")