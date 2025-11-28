import React from 'react';
import RecipeCard from './RecipeCard';

const RecipeList = ({ recipes, loading }) => {
  console.log("🎯 RecipeList reçoit:", recipes);
  
  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        Recherche en cours...
      </div>
    );
  }

  if (!recipes || recipes.length === 0) {
    return (
      <div className="no-results">
        <div className="no-results-icon">🔍</div>
        <h3>Aucune recette trouvée</h3>
        <p>Essayez avec d'autres mots-clés comme "tajine", "couscous", etc.</p>
      </div>
    );
  }

  return (
    <div className="recipes-grid">
      {recipes.map(recipe => (
        <RecipeCard key={recipe.id} recipe={recipe} />
      ))}
    </div>
  );
};

export default RecipeList;