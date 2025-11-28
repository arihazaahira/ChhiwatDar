import { useState, useEffect } from 'react';
import { recipesApi } from '../api/recipesApi';
import recipeImages from '../assets/images';

// Données par défaut des recettes avec les bons imports d'images
const defaultRecipes = [
  {
    id: 1,
    title: "Tajine",
    image: recipeImages.tajine,
    description: "Le tajine est le plat emblématique du Maroc, cuit lentement dans son plat en terre cuite conique."
  },
  {
    id: 2,
    title: "Couscous",
    image: recipeImages.couscous,
    description: "Le plat national du Maroc, servi traditionnellement le vendredi."
  },
  {
    id: 3,
    title: "Bastila",
    image: recipeImages.bastila,
    description: "Une merveille de la cuisine marocaine qui marie le sucré et le salé."
  },
  {
    id: 4,
    title: "Harira",
    image: recipeImages.harira,
    description: "Soupe traditionnelle marocaine riche et réconfortante."
  },
  {
    id: 5,
    title: "Batbout",
    image: recipeImages.batbout,
    description: "Pain marocain moelleux cuit à la poêle."
  },
  {
    id: 6,
    title: "Poulet Marocain",
    image: recipeImages.poulet,
    description: "Poulet aux épices marocaines et olives."
  }
];

export const useRecipes = () => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Charger les recettes au démarrage
  useEffect(() => {
    fetchRecipes();
  }, []);

  const fetchRecipes = async (query = '') => {
    setLoading(true);
    setError(null);
    
    try {
      let data;
      if (query) {
        data = await recipesApi.searchRecipes(query);
      } else {
        data = await recipesApi.getAllRecipes();
      }
      setRecipes(data);
    } catch (error) {
      setError(error.message);
      // Utiliser les données par défaut en cas d'erreur
      if (query) {
        const filtered = defaultRecipes.filter(recipe => 
          recipe.title.toLowerCase().includes(query.toLowerCase()) ||
          recipe.description.toLowerCase().includes(query.toLowerCase())
        );
        setRecipes(filtered);
      } else {
        setRecipes(defaultRecipes);
      }
    }
    setLoading(false);
  };

  return {
    recipes,
    loading,
    error,
    fetchRecipes
  };
};