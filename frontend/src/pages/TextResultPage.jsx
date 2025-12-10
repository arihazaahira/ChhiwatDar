import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import '../styles/ImageResultPage.css';

// 💡 Variable d'environnement pour l'API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''; 

const TextResultPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [recipes, setRecipes] = useState([]);
    const [searchInfo, setSearchInfo] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (location.state) {
            // Récupérer les recettes et les infos de recherche
            if (location.state.matching_recipes) {
                setRecipes(location.state.matching_recipes);
            }
            
            // Stocker les informations de recherche (texte original, traduction, etc.)
            setSearchInfo({
                originalText: location.state.original_text || location.state.text,
                dishName: location.state.dish_name_english,
                query: location.state.query,
                transcription: location.state.transcription,
                translation: location.state.translation
            });
        } else {
            console.error('❌ Aucune donnée trouvée dans location.state');
        }
        setLoading(false);
    }, [location]);

    const handleRecipeClick = (recipeId) => {
        navigate(`/recipe/${recipeId}`);
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Chargement des recettes...</p>
            </div>
        );
    }

    return (
        <div className="text-result-page">
            <Navbar />
            
            <div className="result-container">
                {/* En-tête avec informations de recherche */}
                <section className="search-info-section">
                    <div className="search-info-card">
                        <div className="search-icon">🔍</div>
                        
                    </div>
                </section>

                {/* Section des résultats */}
                <section className="recipes-section">
                    <div className="section-header">
                        <button className="back-btn" onClick={() => navigate('/')}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M19 12H5M12 19l-7-7 7-7"/>
                            </svg>
                            Retour
                        </button>
                        
                        <h2 className="section-title">
                            Recettes trouvées
                            <span className="result-count">({recipes.length})</span>
                        </h2>
                    </div>
                    
                    {recipes.length > 0 ? (
                        <div className="recipes-grid">
                            {recipes.map((recipe, index) => {
                                // Construction de l'URL absolue pour l'image
                                const imageUrl = recipe.image 
                                    ? `${API_BASE_URL}${recipe.image}`
                                    : null;

                                return (
                                    <div 
                                        key={recipe.id || index} 
                                        className="recipe-card"
                                        onClick={() => handleRecipeClick(recipe.id)}
                                    >
                                        {/* Score de correspondance */}
                                        {recipe.match_score && (
                                            <div className="match-score">
                                                <span className="score-icon">⭐</span>
                                                <span className="score-value">
                                                    {recipe.match_score.toFixed(1)}
                                                </span>
                                            </div>
                                        )}

                                        {/* Image de la recette */}
                                        {imageUrl && (
                                            <div className="recipe-image">
                                                <img 
                                                    src={imageUrl} 
                                                    alt={recipe.title || recipe.name}
                                                    onError={(e) => {
                                                        console.error("Erreur de chargement de l'image:", imageUrl);
                                                        e.target.style.display = 'none';
                                                    }}
                                                />
                                            </div>
                                        )}
                                        
                                        {/* Contenu textuel */}
                                        <div className="recipe-content"> 
                                            <h3 className="recipe-title">
                                                {recipe.title || recipe.name || 'Sans titre'}
                                            </h3>
                                            
                                            <p className="recipe-description">
                                                {recipe.description?.substring(0, 120) || 'Aucune description disponible'}...
                                            </p>

                                            {/* Ingrédients principaux */}
                                            {recipe.ingredients && recipe.ingredients.length > 0 && (
                                                <div className="recipe-ingredients">
                                                    <span className="ingredients-label">Ingrédients:</span>
                                                    <div className="ingredients-preview">
                                                        {recipe.ingredients.slice(0, 3).map((ing, idx) => (
                                                            <span key={idx} className="ingredient-preview-item">
                                                                {ing.length > 25 ? ing.substring(0, 25) + '...' : ing}
                                                            </span>
                                                        ))}
                                                        {recipe.ingredients.length > 3 && (
                                                            <span className="ingredients-more">
                                                                +{recipe.ingredients.length - 3} de plus
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                            )}

                                            <button className="view-recipe-btn">
                                                Voir la recette complète
                                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M5 12h14M12 5l7 7-7 7"/>
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="no-results">
                            <div className="no-results-icon">🔍</div>
                            <h3>Aucune recette trouvée</h3>
                            <p>Essayez avec d'autres mots-clés ou reformulez votre recherche</p>
                            <button className="retry-btn" onClick={() => navigate('/')}>
                                Nouvelle recherche
                            </button>
                        </div>
                    )}
                </section>
            </div>

            <Footer />
        </div>
    );
};

export default TextResultPage;