import google.generativeai as genai
from django.conf import settings

# Configurer Gemini avec la clé API depuis settings.py
genai.configure(api_key=settings.GEMINI_API_KEY)

def translate_text(text):
    """
    Envoie le texte à Gemini pour traduction.
    Retourne le texte traduit.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = (
        "This is Moroccan Darija written with French characters. "
        "Extract ONLY the food name mentioned and translate it to English. "
        "Answer with ONLY the dish name in English in lowercase, with no sentences, no punctuation, no explanation. "
        f"Text: {text}"
    )

    response = model.generate_content(prompt)

    return response.text
