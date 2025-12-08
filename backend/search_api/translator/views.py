from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TranslationRequest
from .gemini_service import translate_text
@csrf_exempt
def translate(request):
    if request.method == "POST":
         body = json.loads(request.body.decode('utf-8'))
         text =body.get("text")
         translate =translate_text(text)
         req= TranslationRequest.objects.create(text=text)

         return JsonResponse({
             'message': 'success',
             'translation_id': req.id,
             'text': text,
             'text_Translated': translate
         })
    return JsonResponse({'error': 'Only POST allowed'}, status=400)
