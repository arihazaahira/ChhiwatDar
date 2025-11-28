const API_BASE_URL = 'http://localhost:8000/api';

// Export nommé correct
export const recipesApi = {
  // Récupérer toutes les recettes
  getAllRecipes: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes/`);
      if (!response.ok) throw new Error('Erreur API');
      return await response.json();
    } catch (error) {
      throw new Error('Serveur non disponible');
    }
  },

  // Recherche textuelle
  searchRecipes: async (query) => {
    try {
      const response = await fetch(`${API_BASE_URL}/search/?query=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Erreur API');
      return await response.json();
    } catch (error) {
      throw new Error('Serveur non disponible');
    }
  },

  // Recherche vocale (à adapter selon votre backend)
  voiceSearch: async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    try {
      const response = await fetch(`${API_BASE_URL}/voice-search/`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Erreur API vocale');
      return await response.json();
    } catch (error) {
      throw new Error('Service vocal non disponible');
    }
  },

  // Recherche par image
  imageSearch: async (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
      const response = await fetch(`${API_BASE_URL}/image-search/`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Erreur API image');
      return await response.json();
    } catch (error) {
      throw new Error('Service image non disponible');
    }
  }
};

// Export par défaut également pour plus de flexibilité
export default recipesApi;