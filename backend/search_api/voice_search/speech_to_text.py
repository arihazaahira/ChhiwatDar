from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from google import genai
import tempfile
import os
import time
from dotenv import load_dotenv

load_dotenv()

def parse_response(text):
    """Parse la réponse formatée de Gemini"""
    transcription = text
    translation = None
    
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line.upper().startswith("TRANSCRIPTION:"):
            transcription = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TRANSLATION:"):
            translation = line.split(":", 1)[1].strip()
    
    # Si le format n'est pas respecté, retourner le texte brut
    if transcription == text and "TRANSCRIPTION:" not in text.upper():
        transcription = text
    
    return transcription, translation

@csrf_exempt
def transcribe(request):
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

    gemini_file = None
    
    try:
        # Client Gemini
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Upload vers Gemini
        gemini_file = client.files.upload(file=temp_path)
        
        # Attendre que le fichier soit ACTIVE (polling amélioré)
        max_wait_time = 120  # 2 minutes max
        poll_interval = 2
        elapsed = 0
        
        while elapsed < max_wait_time:
            # Récupérer l'état actuel du fichier
            file_info = client.files.get(name=gemini_file.name)
            state_name = file_info.state.name if hasattr(file_info.state, 'name') else str(file_info.state)
            
            if state_name == "ACTIVE":
                # Fichier prêt, on peut continuer
                gemini_file = file_info  # Mettre à jour avec les infos actuelles
                break
            elif state_name == "FAILED":
                return JsonResponse({"error": "Le traitement du fichier a échoué côté Gemini"}, status=500)
            
            # Attendre avant de re-vérifier
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        if elapsed >= max_wait_time:
            return JsonResponse({"error": "Timeout: le fichier n'a pas pu être traité"}, status=504)

        # Prompt intelligent avec traduction
        prompt = """Tu es un système de transcription et traduction intelligent.

1. Si la langue détectée est l'anglais :
   → transcris normalement en anglais.
   → pas de traduction nécessaire.

2. Si la langue détectée est la darija marocaine :
   → transcris en alphabet latin (lettres françaises).
     Utilise: 3 pour ع, 7 pour ح, 9 pour ق, ch pour ش, gh pour غ, kh pour خ
     Exemple : "salam 3likom", "kifach nta", "chokran bzaf"
   → PUIS traduis en anglais.

3. Sinon (autre langue) :
   → transcris dans la langue détectée.
   → traduis en anglais si ce n'est pas déjà en anglais.

FORMAT DE RÉPONSE (respecte exactement ce format):
TRANSCRIPTION: [le texte transcrit]
TRANSLATION: [la traduction en anglais, ou "N/A" si déjà en anglais]

Exemple pour darija:
TRANSCRIPTION: salam 3likom, kifach nta?
TRANSLATION: Hello, how are you?

Exemple pour anglais:
TRANSCRIPTION: Hello, how are you?
TRANSLATION: N/A"""

        # Essayer plusieurs modèles si nécessaire
        models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        last_error = None
        
        for model_name in models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, gemini_file]
                )
                
                # Parser la réponse
                result_text = response.text.strip()
                transcription, translation = parse_response(result_text)
                
                response_data = {
                    "transcription": transcription,
                    "model": model_name
                }
                
                # Ajouter la traduction si disponible
                if translation and translation.upper() != "N/A":
                    response_data["translation"] = translation
                
                return JsonResponse(response_data)
                
            except Exception as model_error:
                last_error = model_error
                error_str = str(model_error).lower()
                
                # Si c'est une erreur de modèle non disponible, essayer le suivant
                if '404' in error_str or 'not found' in error_str:
                    continue
                
                # Si c'est une autre erreur, attendre et réessayer
                time.sleep(1)
                continue
        
        # Si tous les modèles ont échoué
        return JsonResponse({"error": f"Erreur transcription: {str(last_error)}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    finally:
        # Nettoyage du fichier temporaire local
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        # Nettoyage du fichier sur Gemini
        if gemini_file:
            try:
                client.files.delete(name=gemini_file.name)
            except:
                pass
