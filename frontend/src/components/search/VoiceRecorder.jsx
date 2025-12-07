import React from 'react';
import { useVoiceSearch } from '../../hooks/useVoiceSearch';

const VoiceRecorder = ({ onTranscript, onResults }) => {
  const { 
    isRecording, 
    isProcessing, 
    transcript, 
    results, 
    error, 
    startRecording, 
    stopRecording, 
    cancelRecording 
  } = useVoiceSearch();

  // Envoyer la transcription au parent
  React.useEffect(() => {
    if (transcript && onTranscript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  // Envoyer les résultats au parent
  React.useEffect(() => {
    if (results && results.length > 0 && onResults) {
      onResults(results);
    }
  }, [results, onResults]);

  const handleVoiceClick = async () => {
    if (isRecording) {
      // Arrêter l'enregistrement et rechercher
      try {
        await stopRecording();
      } catch (err) {
        console.error('Erreur lors de l\'arrêt:', err);
      }
    } else {
      // Démarrer l'enregistrement
      try {
        await startRecording();
      } catch (err) {
        console.error('Erreur lors du démarrage:', err);
      }
    }
  };

  const handleCancel = () => {
    cancelRecording();
  };

  return (
    <div className="voice-recorder">
      <button 
        className={`voice-btn ${isRecording ? 'active recording' : ''} ${isProcessing ? 'processing' : ''}`} 
        onClick={handleVoiceClick}
        disabled={isProcessing}
        title={
          isProcessing ? 'Traitement en cours...' :
          isRecording ? 'Arrêter et rechercher' : 
          'Démarrer la recherche vocale'
        }
      >
        <svg 
          className="voice-icon" 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          {isRecording ? (
            // Icône Stop
            <rect x="6" y="6" width="12" height="12" rx="2" />
          ) : (
            // Icône Microphone
            <>
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="22"></line>
            </>
          )}
        </svg>
        
        {isProcessing && <span className="processing-text">⏳</span>}
        {isRecording && <span className="recording-indicator">🔴</span>}
      </button>

      {/* Bouton d'annulation si en cours d'enregistrement */}
      {isRecording && (
        <button 
          className="cancel-btn" 
          onClick={handleCancel}
          title="Annuler l'enregistrement"
        >
          ❌
        </button>
      )}

      {/* Affichage des erreurs */}
      {error && <span className="error-tooltip">{error}</span>}

      {/* Affichage de la transcription */}
      {transcript && (
        <div className="transcript-preview">
          <strong>Vous avez dit :</strong> "{transcript}"
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;