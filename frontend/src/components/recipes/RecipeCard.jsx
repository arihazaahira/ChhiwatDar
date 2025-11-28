import React from 'react';

const RecipeCard = ({ recipe }) => {
  const handleImageError = (e) => {
    e.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=250&fit=crop';
    e.target.alt = 'Image non disponible';
  };

  return (
    <div className="recipe-card">
      <img 
        src={recipe.image} 
        alt={recipe.title}
        className="recipe-image"
        onError={handleImageError}
      />
      <div className="recipe-content">
        <h3>{recipe.title}</h3>
        <p>{recipe.description}</p>
      </div>
    </div>
  );
};

export default RecipeCard;