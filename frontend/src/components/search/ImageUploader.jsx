import React, { useRef } from 'react';

const ImageUploader = ({ onImageSelect, onImageAnalysis }) => {
  const fileInputRef = useRef(null);

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      if (onImageAnalysis) {
        onImageAnalysis('Analyse de l\'image...');
      }
      
      // Simulation d'analyse d'image
      setTimeout(() => {
        if (onImageSelect) {
          onImageSelect('tajine');
        }
        if (onImageAnalysis) {
          onImageAnalysis('Image analysée - recherche pour "tajine"');
        }
      }, 1000);
    }
  };

  return (
    <>
      <button className="camera-btn" onClick={handleImageClick}>
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
      />
    </>
  );
};

export default ImageUploader;