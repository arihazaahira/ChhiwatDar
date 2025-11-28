import React from 'react';
import { useNavigate } from 'react-router-dom';

const RecipeCard = ({ recipe }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/recipe/${recipe.id}`);
  };

  const handleImageError = (e) => {
    e.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=250&fit=crop';
  };

  return (
    <div className="recipe-card" onClick={handleClick}>
      <img 
        src={recipe.image} 
        alt={recipe.title}
        className="recipe-image"
        onError={handleImageError}
      />
      <div className="recipe-content">
        <h3>{recipe.title}</h3>
        <p className="recipe-description">{recipe.description}</p>
        
        {(recipe.temps_cuisson || recipe.difficulte) && (
          <div className="recipe-details">
            {recipe.temps_cuisson && (
              <span className="detail-item">⏱️ {recipe.temps_cuisson}</span>
            )}
            {recipe.difficulte && (
              <span className="detail-item">⚡ {recipe.difficulte}</span>
            )}
          </div>
        )}
        
        <div className="recipe-click-hint">
          Cliquer pour voir les détails →
        </div>
      </div>
    </div>
  );
};

export default RecipeCard;