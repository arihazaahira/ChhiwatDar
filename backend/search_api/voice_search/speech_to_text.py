"""
Module de transcription audio avec Gemini API (nouvelle syntaxe Client)
Utilise gemini-2.5-flash (modèle qui fonctionne avec google-genai)
"""

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
import tempfile
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ✅ MODÈLE CORRECT pour l'API google-genai
MODEL_NAME = "gemini-2.5-flash"

def parse_response(text):
    """Parse la réponse formatée de Gemini"""
    transcription = text
    translation = None
    
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line.upper().startswith("TRANSCRIPTION:"):
            transcription = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TRANSLATION:") or line.upper().startswith("TRADUCTION:"):
            translation = line.split(":", 1)[1].strip()
    
    # Si le format n'est pas respecté, retourner le texte brut
    if transcription == text and "TRANSCRIPTION:" not in text.upper():
        transcription = text
    
    return transcription, translation

@csrf_exempt
def transcribe(request):
    """
    Transcrit un fichier audio avec Gemini Client API
    Darija → alphabet latin + traduction ANGLAIS
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    # Vérifier le fichier
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({"error": "Aucun fichier envoyé"}, status=400)

    # Obtenir l'extension du fichier
    file_ext = audio_file.name.split('.')[-1].lower() if '.' in audio_file.name else 'webm'
    
    # Sauvegarder temporairement
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp:
        for chunk in audio_file.chunks():
            temp.write(chunk)
        temp_path = temp.name

    uploaded_file = None
    client = None
    
    try:
        # ✅ NOUVELLE SYNTAXE : Client API (comme speachV2.py)
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Upload du fichier via client.files.upload()
        print(f"📤 Upload du fichier: {temp_path}")
        uploaded_file = client.files.upload(file=temp_path)
        print(f"✅ Fichier uploadé: {uploaded_file.name}")
        
        # Attendre que le fichier soit ACTIVE
        max_wait_time = 120  # 2 minutes max
        poll_interval = 2
        elapsed = 0
        
        while elapsed < max_wait_time:
            file_info = client.files.get(name=uploaded_file.name)
            
            if file_info.state == "ACTIVE":
                print(f"✅ Fichier ACTIVE")
                break
            elif file_info.state == "FAILED":
                return JsonResponse({
                    "error": "Le traitement du fichier a échoué côté Gemini",
                    "success": False
                }, status=500)
            
            print(f"⏳ État: {file_info.state}, attente...")
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        if elapsed >= max_wait_time:
            return JsonResponse({
                "error": "Timeout: le fichier n'a pas pu être traité",
                "success": False
            }, status=504)

        # ✅ PROMPT MODIFIÉ : Traduction vers ANGLAIS pour Darija
        prompt = """Tu es un système de transcription et traduction intelligent.

1. Si la langue détectée est l'anglais :
   → transcris normalement en anglais.
   → pas de traduction nécessaire (réponds "N/A" pour TRANSLATION).

2. Si la langue détectée est la darija marocaine :
   → transcris en alphabet latin (lettres françaises).
     Utilise: 3 pour ع, 7 pour ح, 9 pour ق, ch pour ش, gh pour غ, kh pour خ
     Exemple : "salam 3likom", "kifach nta", "chokran bzaf"
   → PUIS traduis en ANGLAIS.

3. Si la langue détectée est le français :
   → transcris normalement en français.
   → traduis en ANGLAIS.

4. Sinon (autre langue) :
   → transcris dans la langue détectée.
   → traduis en ANGLAIS.

FORMAT DE RÉPONSE (respecte exactement ce format):
TRANSCRIPTION: [le texte transcrit]
TRANSLATION: [la traduction en anglais, ou "N/A" si déjà en anglais]

Exemple pour darija:
TRANSCRIPTION: salam 3likom, kifach nta?
TRANSLATION: Hello, how are you?

Exemple pour anglais:
TRANSCRIPTION: Hello, how are you?
TRANSLATION: N/A

Exemple pour français:
TRANSCRIPTION: Bonjour, comment allez-vous?
TRANSLATION: Hello, how are you?"""

        # ✅ CORRECTION : Utiliser la même syntaxe que speachV2.py
        print(f"🎙️ Transcription en cours avec {MODEL_NAME}...")
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, uploaded_file],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT']
            )
        )
        
        # Parser la réponse
        result_text = response.text.strip()
        print("="*60)
        print(result_text)
        print("="*60)
        
        transcription, translation = parse_response(result_text)
        
        response_data = {
            "transcription": transcription,
            "model": MODEL_NAME,
            "success": True
        }
        
        # Ajouter la traduction si disponible
        if translation and translation.upper() != "N/A":
            response_data["translation"] = translation
        
        return JsonResponse(response_data)

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur: {error_msg}")
        
        # Message d'erreur plus clair pour le quota
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return JsonResponse({
                "error": "Quota API dépassé. Veuillez réessayer dans quelques minutes.",
                "details": "Le modèle Gemini a atteint sa limite. Réessayez plus tard.",
                "success": False
            }, status=429)
        
        # Message d'erreur pour modèle non trouvé
        if "404" in error_msg or "NOT_FOUND" in error_msg:
            return JsonResponse({
                "error": "Modèle non disponible.",
                "details": f"Le modèle {MODEL_NAME} n'est pas accessible. Vérifiez votre API key.",
                "success": False
            }, status=404)
        
        return JsonResponse({
            "error": f"Erreur: {error_msg}",
            "success": False
        }, status=500)
    
    finally:
        # Nettoyage du fichier temporaire local
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print(f"🗑️ Fichier local supprimé")
            except Exception as e:
                print(f"⚠️ Erreur suppression locale: {e}")
        
        # Nettoyage du fichier sur Gemini
        if uploaded_file and client:
            try:
                client.files.delete(name=uploaded_file.name)
                print(f"🗑️ Fichier Gemini supprimé")
            except Exception as e:
                print(f"⚠️ Erreur suppression Gemini: {e}")