import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import DetailsRecipe from './pages/DetailsRecipe';

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/recipe/:id" element={<DetailsRecipe />} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;