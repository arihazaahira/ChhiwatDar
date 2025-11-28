import React from 'react';
import { useVoiceSearch } from '../../hooks/useVoiceSearch';

const VoiceRecorder = ({ onTranscript }) => {
  const { isListening, transcript, error, startListening, stopListening } = useVoiceSearch();

  React.useEffect(() => {
    if (transcript && onTranscript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  const handleVoiceClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <button 
      className={`voice-btn ${isListening ? 'active listening' : ''}`} 
      onClick={handleVoiceClick}
      title={isListening ? 'Arrêter la reconnaissance vocale' : 'Recherche vocale'}
    >
      <svg className="voice-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="22"></line>
      </svg>
      {error && <span className="error-tooltip">{error}</span>}
    </button>
  );
};

export default VoiceRecorder;