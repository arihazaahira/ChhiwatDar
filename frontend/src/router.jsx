import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import ImageResultPage from './pages/ImageResultPage';  // ← Vérifiez ce chemin
import CreateRecipePage from './pages/CreateRecipePage';
import RecipeDetails from './pages/RecipeDetails'; // Ajoutez cette importation

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/recipe/:id" element={<RecipeDetails />} />
        <Route path="/image-result" element={<ImageResultPage />} />
        <Route path="/create-recipe" element={<CreateRecipePage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;