const API_BASE_URL = 'http://localhost:8000/api';

export const recipesApi = {
  getAllRecipes: async () => {
    const response = await fetch(`${API_BASE_URL}/recipes/`);
    return response.json();
  },

  searchRecipes: async (query) => {
    const response = await fetch(`${API_BASE_URL}/search/?query=${encodeURIComponent(query)}`);
    return response.json();
  },

  getRecipeDetails: async (recipeId) => {
    const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/`);
    return response.json();
  }
};