import React from 'react';
import RecipeCard from './RecipeCard';

const RecipeList = ({ recipes, loading }) => {
  if (loading) {
    return <div className="loading">Chargement...</div>;
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