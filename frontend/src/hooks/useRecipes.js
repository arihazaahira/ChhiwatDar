import { useState, useEffect, useCallback } from 'react';
import { recipesApi } from '../api/recipesApi';
import recipeImages from '../assets/images';

// Données par défaut avec les images locales
const defaultRecipes = [
  {
    id: 1,
    title: "Tajine de Poulet aux Citrons Confits",
    image: recipeImages.tajine,  // ← Image locale
    description: "Un plat marocain emblématique cuit lentement avec des citrons confits et des olives.",
    ingredients: ["poulet", "citrons confits", "olives", "oignons", "ail", "gingembre", "safran"],
    temps_cuisson: "90 minutes",
    difficulte: "Moyenne"
  },
  {
    id: 2,
    title: "Couscous aux Légumes",
    image: recipeImages.couscous,  // ← Image locale
    description: "Le plat traditionnel du vendredi, avec de la semoule et des légumes frais.",
    ingredients: ["semoule", "carottes", "courgettes", "navets", "pois chiches", "agneau"],
    temps_cuisson: "120 minutes",
    difficulte: "Facile"
  },
  {
    id: 3,
    title: "Bastila au Poulet",
    image: recipeImages.bastila,  // ← Image locale
    description: "Feuilleté sucré-salé typique de la cuisine marocaine.",
    ingredients: ["poulet", "amandes", "oignons", "œufs", "sucre", "cannelle", "feuilles de brick"],
    temps_cuisson: "60 minutes",
    difficulte: "Difficile"
  },
  {
    id: 4,
    title: "Harira Marocaine",
    image: recipeImages.harira,  // ← Image locale
    description: "Soupe traditionnelle pour le Ramadan, riche et nourrissante.",
    ingredients: ["lentilles", "tomates", "agneau", "pois chiches", "coriandre", "persil"],
    temps_cuisson: "45 minutes",
    difficulte: "Facile"
  },
  {
    id: 5,
    title: "Batbout Maison",
    image: recipeImages.batbout,  // ← Image locale
    description: "Pain marocain moelleux cuit à la poêle.",
    ingredients: ["farine", "semoule", "levure", "sel", "eau"],
    temps_cuisson: "30 minutes",
    difficulte: "Facile"
  },
  {
    id: 6,
    title: "Poulet aux Olives et Citron",
    image: recipeImages.poulet,  // ← Image locale
    description: "Poulet mijoté avec des olives vertes et du citron.",
    ingredients: ["poulet", "olives vertes", "citron", "ail", "gingembre", "safran"],
    temps_cuisson: "60 minutes",
    difficulte: "Moyenne"
  }
];

export const useRecipes = () => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecipes = useCallback(async (query = '') => {
    setLoading(true);
    setError(null);
    
    try {
      let data;
      if (query) {
        console.log("🔍 Recherche API pour:", query);
        data = await recipesApi.searchRecipes(query);
        
        // Si le backend ne retourne pas d'images, on les ajoute
        data = data.map(recipe => {
          const defaultRecipe = defaultRecipes.find(r => r.id === recipe.id);
          return {
            ...recipe,
            image: recipe.image || (defaultRecipe ? defaultRecipe.image : recipeImages.tajine)
          };
        });
        
      } else {
        console.log("📦 Chargement de toutes les recettes");
        data = await recipesApi.getAllRecipes();
        
        // Si le backend ne retourne pas d'images, utiliser les données locales
        if (!data || data.length === 0 || !data[0].image) {
          console.log("🖼️ Utilisation des images locales");
          data = defaultRecipes;
        } else {
          // S'assurer que toutes les recettes ont une image
          data = data.map(recipe => ({
            ...recipe,
            image: recipe.image || recipeImages.tajine
          }));
        }
      }
      
      console.log("📊 Données finales à afficher:", data);
      setRecipes(data);
      
    } catch (error) {
      console.error("❌ Erreur API:", error);
      setError(error.message);
      
      // Fallback aux données locales avec images
      console.log("🔄 Utilisation des données locales avec images");
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
  }, []);

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  return {
    recipes,
    loading,
    error,
    fetchRecipes
  };
};