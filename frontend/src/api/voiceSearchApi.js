const API_BASE_URL = 'http://localhost:8000/api';

export const voiceSearchApi = {
  /**
   * Envoie un fichier audio au backend Django pour transcription et recherche
   * @param {Blob} audioBlob - Le fichier audio enregistré
   * @returns {Promise} - Résultat avec transcription et recettes
   */
  searchByVoice: async (audioBlob) => {
    try {
      // Créer un FormData pour envoyer le fichier
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch(`${API_BASE_URL}/voice-search/`, {
        method: 'POST',
        body: formData,
        // Ne pas définir Content-Type, le navigateur le fera automatiquement avec boundary
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erreur lors de la recherche vocale');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur API voiceSearch:', error);
      throw error;
    }
  },

  /**
   * Transcrit uniquement l'audio sans faire de recherche
   * @param {Blob} audioBlob - Le fichier audio enregistré
   * @returns {Promise} - Texte transcrit
   */
  transcribeAudio: async (audioBlob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch(`${API_BASE_URL}/transcribe/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la transcription');
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur transcription:', error);
      throw error;
    }
  }
};