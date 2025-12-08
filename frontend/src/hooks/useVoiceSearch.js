import { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { voiceSearchApi } from '../api/voiceSearchApi';
import { AudioRecorderService } from '../services/audioService';

export const useVoiceSearch = () => {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');
  
  const recorderRef = useRef(new AudioRecorderService());

  /**
   * Démarre l'enregistrement vocal
   */
  const startRecording = useCallback(async () => {
    try {
      setError('');
      setTranscript('');
      setResults([]);
      
      const recorder = recorderRef.current;
      
      if (!recorder.isSupported()) {
        throw new Error('Enregistrement audio non supporté par votre navigateur');
      }

      await recorder.startRecording();
      setIsRecording(true);
    } catch (err) {
      setError(err.message || 'Erreur lors du démarrage de l\'enregistrement');
      console.error('Erreur startRecording:', err);
    }
  }, []);

  /**
   * Arrête l'enregistrement et envoie au backend Django
   */
  const stopRecording = useCallback(async () => {
    try {
      setIsRecording(false);
      setIsProcessing(true);
      
      const recorder = recorderRef.current;
      const audioBlob = await recorder.stopRecording();

      // Envoyer au backend Django
      const response = await voiceSearchApi.searchByVoice(audioBlob);
      
      // Mettre à jour l'état local
      setTranscript(response.transcription || '');
      setResults(response.results || []);
      setIsProcessing(false);

      // ✅ NAVIGATION VERS LA PAGE DE RÉSULTATS
      if (response.success && response.matching_recipes) {
        navigate('/voice-results', {
          state: {
            matching_recipes: response.matching_recipes,
            transcription: response.transcription,
            translation: response.translation,
            analysis_result: response.analysis_result,
            count: response.count,
            query: response.query,
            model: response.model || 'unknown'
          }
        });
      } else if (response.results && response.results.length > 0) {
        // Fallback pour l'ancien format de réponse
        navigate('/voice-results', {
          state: {
            matching_recipes: response.results,
            transcription: response.transcription || response.query,
            count: response.results.length,
            query: response.query
          }
        });
      }

      return response;
    } catch (err) {
      setError(err.message || 'Erreur lors du traitement audio');
      setIsProcessing(false);
      console.error('Erreur stopRecording:', err);
      throw err;
    }
  }, [navigate]); // ✅ Ajouter navigate aux dépendances

  /**
   * Annule l'enregistrement en cours
   */
  const cancelRecording = useCallback(() => {
    recorderRef.current.cancelRecording();
    setIsRecording(false);
    setError('');
  }, []);

  /**
   * Réinitialise l'état
   */
  const reset = useCallback(() => {
    setTranscript('');
    setResults([]);
    setError('');
  }, []);

  return {
    isRecording,
    isProcessing,
    transcript,
    results,
    error,
    startRecording,
    stopRecording,
    cancelRecording,
    reset
  };
};