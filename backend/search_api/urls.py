"""
Configuration des URLs pour l'application de recettes
CORRECTION FINALE: Suppression des doublons et ordre correct des routes
"""

from django.urls import path
from . import views
from .voice_search.speech_to_text import transcribe

urlpatterns = [
    # Liste de toutes les recettes
    path('recipes/', views.get_all_recipes, name='get_all_recipes'),
    
    # Recherche de recettes
    path('search/', views.search_recipes, name='search_recipes'),
    
    # Analyse d'image avec Gemini (AVANT les routes dynamiques)
    path('analyze-image/', views.analyze_recipe_image, name='analyze_recipe_image'),
    
    # Recettes créées par les utilisateurs (AVANT les routes dynamiques)
    path('recipes/create/', views.create_user_recipe, name='create_user_recipe'),
    path('recipes/user/', views.get_user_recipes, name='get_user_recipes'),
    
    # 🔧 ROUTE DYNAMIQUE POUR LES DÉTAILS (doit être EN DERNIER)
    # Utilise <str:recipe_id> pour accepter "16_tajine_poulet" et pas seulement "16"
    path('recipes/<str:recipe_id>/', views.get_recipe_details, name='get_recipe_details'),
    
]