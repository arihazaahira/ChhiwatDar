from django.urls import path
from . import views

urlpatterns = [
    path('recipes/', views.get_all_recipes, name='get_all_recipes'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('recipes/<int:recipe_id>/', views.get_recipe_details, name='get_recipe_details'),
    path('analyze-image/', views.analyze_recipe_image, name='analyze_recipe_image'),
    path('recipes/create/', views.create_user_recipe, name='create_user_recipe'),
    path('recipes/user/', views.get_user_recipes, name='get_user_recipes'),
]