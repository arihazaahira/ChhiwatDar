import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import '../styles/RecipeDetails.css';

// 💡 1. IMPORTER LA VARIABLE D'ENVIRONNEMENT VITE
// On utilise import.meta.env pour accéder aux variables préfixées par VITE_
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''; 

const RecipeDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [recipe, setRecipe] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        console.log('🔍 RecipeDetails - ID de la recette:', id);
        fetchRecipeDetails();
    }, [id]);

    const fetchRecipeDetails = async () => {
        try {
            setLoading(true);
            // 💡 NOTA BENE : L'appel d'API est correct car vous utilisez déjà 'http://localhost:8000'
            const response = await fetch(`http://localhost:8000/api/recipes/${id}/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();

            if (data.success) {
                setRecipe(data.recipe);
            } else {
                setError(data.error || 'Recette non trouvée');
            }
        } catch (err) {
            console.error('❌ Erreur:', err);
            setError('Erreur de chargement de la recette');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Chargement de la recette...</p>
            </div>
        );
    }

    if (error || !recipe) {
        return (
            <div className="error-container">
                <Navbar />
                <div className="error-content">
                    <h2>😕 Oups !</h2>
                    <p>{error || 'Recette non trouvée'}</p>
                    <button onClick={() => navigate('/')}>
                        Retour à l'accueil
                    </button>
                </div>
                <Footer />
            </div>
        );
    }

    // 💡 2. CONSTRUCTION DE L'URL ABSOLUE AVANT LE RENDU
    // Si recipe.image est '/media/harira.jpeg', on ajoute l'URL de base
    const imageUrl = recipe.image 
        ? `${API_BASE_URL}${recipe.image}`
        : null;


    return (
        <div className="recipe-details-page">
            <Navbar />
            
            <div className="recipe-container">
                {/* Header avec image */}
                <section className="recipe-header">
                    <button className="back-btn" onClick={() => navigate(-1)}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M19 12H5M12 19l-7-7 7-7"/>
                        </svg>
                        Retour
                    </button>

                    <div className="recipe-hero">
                        {/* 💡 3. UTILISER L'URL ABSOLUE CONSTRUITE */}
                        {imageUrl && ( 
                            <div className="recipe-hero-image">
                                <img 
                                    src={imageUrl} // <-- C'est ici qu'on utilise l'URL complète
                                    alt={recipe.title || recipe.name}
                                    onError={(e) => {
                                        console.error("Erreur de chargement de l'image:", imageUrl);
                                        e.target.src = '/placeholder-recipe.jpg'; // Fallback
                                    }}
                                />
                            </div>
                        )}
                        
                        <div className="recipe-hero-content">
                            <h1 className="recipe-title">
                                {recipe.title || recipe.name}
                            </h1>
                            
                            {/* ... (Le reste du contenu de la recette est inchangé) ... */}

                            {recipe.description && (
                                <p className="recipe-description">
                                    {recipe.description}
                                </p>
                            )}

                            {recipe.author && (
                                <div className="recipe-author">
                                    <span className="author-label">Par:</span>
                                    <span className="author-name">
                                        {recipe.author.name || 'Chef Anonyme'}
                                    </span>
                                </div>
                            )}

                            {recipe.created_at && (
                                <div className="recipe-date">
                                    <span className="date-label">Créé le:</span>
                                    <span className="date-value">
                                        {new Date(recipe.created_at).toLocaleDateString('fr-FR')}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                {/* Ingrédients */}
                <section className="recipe-section ingredients-section">
                    <h2 className="section-title">
                        <span className="section-icon">🥘</span>
                        Ingrédients
                    </h2>
                    
                    {recipe.ingredients && recipe.ingredients.length > 0 ? (
                        <ul className="ingredients-list">
                            {recipe.ingredients.map((ingredient, index) => (
                                <li key={index} className="ingredient-item">
                                    <span className="ingredient-bullet">◆</span>
                                    <span className="ingredient-text">{ingredient}</span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="no-data">Aucun ingrédient disponible</p>
                    )}
                </section>

                {/* Préparation */}
                <section className="recipe-section steps-section">
                    <h2 className="section-title">
                        <span className="section-icon">👨‍🍳</span>
                        Étapes de préparation
                    </h2>
                    
                    {recipe.steps && recipe.steps.length > 0 ? (
                        <ol className="steps-list">
                            {recipe.steps.map((step, index) => (
                                <li key={index} className="step-item">
                                    <div className="step-number">{index + 1}</div>
                                    <div className="step-content">
                                        <p className="step-text">{step}</p>
                                    </div>
                                </li>
                            ))}
                        </ol>
                    ) : (
                        <p className="no-data">Aucune étape de préparation disponible</p>
                    )}
                </section>

                {/* Informations supplémentaires */}
                <div className="recipe-info-grid">
                    {recipe.prep_time && (
                        <div className="info-card">
                            <span className="info-icon">⏱️</span>
                            <div className="info-content">
                                <span className="info-label">Temps de préparation</span>
                                <span className="info-value">{recipe.prep_time}</span>
                            </div>
                        </div>
                    )}
                    
                    {recipe.cook_time && (
                        <div className="info-card">
                            <span className="info-icon">🔥</span>
                            <div className="info-content">
                                <span className="info-label">Temps de cuisson</span>
                                <span className="info-value">{recipe.cook_time}</span>
                            </div>
                        </div>
                    )}
                    
                    {recipe.servings && (
                        <div className="info-card">
                            <span className="info-icon">👥</span>
                            <div className="info-content">
                                <span className="info-label">Portions</span>
                                <span className="info-value">{recipe.servings}</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default RecipeDetails;