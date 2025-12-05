from django.urls import path
from . import views
from .voice_search.speech_to_text import transcribe

urlpatterns = [
    path('recipes/', views.get_all_recipes, name='get_all_recipes'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('recipes/<int:recipe_id>/', views.get_recipe_details, name='get_recipe_details'),
    path('voice-search/transcribe/', transcribe, name='transcribe'),
]