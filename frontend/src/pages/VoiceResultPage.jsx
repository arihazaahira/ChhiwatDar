import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import '../styles/VoiceResultPage.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const VoiceResultPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [detectedDish, setDetectedDish] = useState('');

    useEffect(() => {
        if (location.state) {
            console.log("📊 Données reçues dans VoiceResultPage:", location.state);
            
            // Extraire les données de recherche vocale
            if (location.state.matching_recipes) {
                setRecipes(location.state.matching_recipes);
            }
            
            // Récupérer la requête de recherche (transcription)
            const query = location.state.transcription || 
                         location.state.query || 
                         (location.state.analysis_result?.nom_recette ? `Recherche pour "${location.state.analysis_result.nom_recette}"` : 'Recherche vocale');
            
            setSearchQuery(query);
            
            // Récupérer le plat détecté si disponible
            if (location.state.analysis_result?.nom_recette) {
                setDetectedDish(location.state.analysis_result.nom_recette);
            }
        } else {
            console.error('❌ Aucune donnée trouvée dans location.state');
        }
        setLoading(false);
    }, [location]);

    const handleRecipeClick = (recipeId) => {
        navigate(`/recipe/${recipeId}`);
    };

    const getSearchSummary = () => {
        if (detectedDish && detectedDish !== 'plat marocain') {
            return `Recettes de "${detectedDish}"`;
        }
        
        if (searchQuery && searchQuery.length > 0) {
            return `Recettes correspondant à "${searchQuery}"`;
        }
        
        return 'Résultats de recherche vocale';
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Chargement des résultats de recherche vocale...</p>
            </div>
        );
    }

    return (
        <div className="voice-result-page">
            <Navbar />
            
            <div className="result-container">
                <section className="voice-results-section">
                    <div className="section-header">
                        <button className="back-btn" onClick={() => navigate('/')}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M19 12H5M12 19l-7-7 7-7"/>
                            </svg>
                            Nouvelle recherche 
                        </button>
                        
                        <div className="search-header">
                            {/* Icône microphone stylée */}
                            <div className="voice-icon-container">
                                <svg className="voice-icon" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                                    <line x1="12" y1="19" x2="12" y2="23"/>
                                    <line x1="8" y1="23" x2="16" y2="23"/>
                                </svg>
                            </div>
                            
                            <div className="search-info">
                                <h2 className="section-title">
                                    {getSearchSummary()}
                                    <span className="result-count">({recipes.length})</span>
                                </h2>
                                
                                {/* Badge de recherche vocale */}
                                
                            </div>
                        </div>
                    </div>
                    
                    {recipes.length > 0 ? (
                        <>
                            {/* Affichage minimal des détections */}
                            <div className="detection-summary">
                                {detectedDish && detectedDish !== 'plat marocain' && (
                                    <div className="detection-chip">
                                        <span className="chip-icon">🍽️</span>
                                        <span className="chip-text">Plat: <strong>{detectedDish}</strong></span>
                                    </div>
                                )}
                            </div>
                            
                            {/* Grid des recettes */}
                            <div className="recipes-grid">
                                {recipes.map((recipe, index) => {
                                    const imageUrl = recipe.image 
                                        ? `${API_BASE_URL}${recipe.image}`
                                        : null;

                                    return (
                                        <div 
                                            key={recipe.id || index} 
                                            className="recipe-card"
                                            onClick={() => handleRecipeClick(recipe.id)}
                                        >
                                            <div className="match-score">
                                                <span className="score-icon">⭐</span>
                                                <span className="score-value">
                                                    {recipe.match_score?.toFixed(1) || '0.0'}
                                                </span>
                                            </div>

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
                                            
                                            <div className="recipe-content"> 
                                                <h3 className="recipe-title">
                                                    {recipe.title || recipe.name || 'Sans titre'}
                                                </h3>
                                                
                                                <p className="recipe-description">
                                                    {recipe.description?.substring(0, 120) || 'Aucune description disponible'}...
                                                </p>

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
                        </>
                    ) : (
                        <div className="no-results">
                            <div className="no-results-icon">🔍</div>
                            <h3>Aucune recette trouvée</h3>
                            <p>Essayez avec une autre recherche vocale plus précise</p>
                            <div className="voice-tips">
                                <h4>Conseils pour une meilleure recherche :</h4>
                                <ul>
                                    <li>Nommez clairement le plat marocain (ex: "tajine", "couscous")</li>
                                    <li>Ajoutez des ingrédients principaux (ex: "poulet aux olives et citron")</li>
                                    <li>Parlez dans un environnement calme</li>
                                    <li>Énoncez à un rythme normal</li>
                                </ul>
                            </div>
                            <button className="retry-btn" onClick={() => navigate('/voice-search')}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                                    <line x1="12" y1="19" x2="12" y2="23"/>
                                    <line x1="8" y1="23" x2="16" y2="23"/>
                                </svg>
                                Nouvelle recherche vocale
                            </button>
                        </div>
                    )}
                </section>
            </div>

            <Footer />
        </div>
    );
};

export default VoiceResultPage;