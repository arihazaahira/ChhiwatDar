from google import genai
from google.genai import types
from PIL import Image
import os

# Clé API stockée dans une variable d'environnement
client = genai.Client(api_key="AIzaSyC8IWjx3f6oDHiGy_VyUu-8cM_t1B0FMxU")

# Chemin vers ton image locale
image_path = "couscous.jpeg"
image = Image.open(image_path)

# Prompt pour reconnaissance du plat marocain
prompt = """
Analyse cette image et renvoie uniquement une **liste JSON** avec :
1. "nom_recette" : le nom du plat marocain que tu reconnais.
2.  en anglais "ingredients_visibles" : une liste des ingrédients que tu vois dans l'image.

Réponds uniquement en JSON, pas de texte supplémentaire.
"""

# Appel du modèle multimodal
response = client.models.generate_content(
    model="gemini-2.5-flash",  # ou gemini-1.5-pro selon ce qui est dispo
    contents=[prompt, image],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT']
    )
)

print("Réponse :", response.text)
