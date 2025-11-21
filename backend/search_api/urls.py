from django.urls import path
from . import views

urlpatterns = [
    path('recipes/', views.recipe_list, name='recipe-list'),
    path('search/', views.search_recipes, name='search-recipes'),
    # SUPPRIMEZ ou COMMENTEZ cette ligne si la fonction n'existe pas :
    # path('search-by-image/', views.search_by_image, name='search-by-image'),
]