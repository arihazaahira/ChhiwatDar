export class AudioRecorderService {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.stream = null;
  }

  /**
   * Vérifie si le navigateur supporte l'enregistrement audio
   */
  isSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  /**
   * Démarre l'enregistrement audio
   */
  async startRecording() {
    try {
      // Demander l'accès au microphone
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });

      // Créer le MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.stream);
      this.audioChunks = [];

      // Stocker les chunks audio
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      // Démarrer l'enregistrement
      this.mediaRecorder.start();
      
      return true;
    } catch (error) {
      console.error('Erreur lors du démarrage:', error);
      throw new Error('Impossible d\'accéder au microphone');
    }
  }

  /**
   * Arrête l'enregistrement et retourne le Blob audio
   */
  async stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        reject(new Error('Aucun enregistrement en cours'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        // Créer un Blob à partir des chunks
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        
        // Nettoyer
        this.cleanup();
        
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Annule l'enregistrement
   */
  cancelRecording() {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
    this.cleanup();
  }

  /**
   * Nettoie les ressources
   */
  cleanup() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    this.audioChunks = [];
    this.mediaRecorder = null;
  }

  /**
   * Vérifie si l'enregistrement est en cours
   */
  isRecording() {
    return this.mediaRecorder && this.mediaRecorder.state === 'recording';
  }
}

// Export une instance par défaut
export const audioRecorder = new AudioRecorderService();