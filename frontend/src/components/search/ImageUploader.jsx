import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ImageUploader = ({ onImageSelect, onImageAnalysis }) => {
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsAnalyzing(true);
    if (onImageAnalysis) {
      onImageAnalysis('Analyse de l\'image avec l\'IA...');
    }

    try {
      // Créer une preview de l'image
      const imagePreview = URL.createObjectURL(file);

      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('http://localhost:8000/api/analyze-image/', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success && result.data) {
        console.log('✅ Navigation vers /image-result avec:', result.data);
        
        // Naviguer vers la page de résultats
        navigate('/image-result', {
          state: {
            analysisResult: result.data,
            imagePreview: imagePreview
          }
        });
        
        // Alternative si navigate ne fonctionne pas
        // window.location.href = '/image-result';
      } else {
        if (onImageAnalysis) {
          onImageAnalysis('Erreur lors de l\'analyse');
        }
      }
    } catch (error) {
      console.error('Erreur:', error);
      if (onImageAnalysis) {
        onImageAnalysis('Erreur de connexion');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <>
      <button className="camera-btn" onClick={handleImageClick} disabled={isAnalyzing}>
        <svg className="camera-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="9" cy="9" r="2"></circle>
          <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
        </svg>
      </button>
      <input 
        type="file" 
        ref={fileInputRef} 
        className="image-input" 
        accept="image/*" 
        onChange={handleImageChange} 
        style={{ display: 'none' }}
        disabled={isAnalyzing}
      />
    </>
  );
};

export default ImageUploader;