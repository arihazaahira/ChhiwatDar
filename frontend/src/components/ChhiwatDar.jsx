import React, { useState, useRef, useEffect } from 'react';
import "../css/ChhiwatDar.css";

// Importez vos images avec des noms plus simples
import tajineImage from "../assets/tagine.jpeg";
import couscousImage from "../assets/couscous.jpeg";
import bastilaImage from "../assets/bastila.jpeg";
import hariraImage from "../assets/harira.jpeg";
import batboutImage from "../assets/batbout.jpeg";
import pouletImage from "../assets/poulet.jpeg";
const ChhiwatDar = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchStatus, setSearchStatus] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef(null);

    // Données par défaut des recettes
    const defaultRecipes = [
        {
            id: 1,
            title: "Tajine",
            image: tajineImage,
            description: "Le tajine est le plat emblématique du Maroc, cuit lentement dans son plat en terre cuite conique."
        },
        {
            id: 2,
            title: "Couscous",
            image: couscousImage,
            description: "Le plat national du Maroc, servi traditionnellement le vendredi."
        },
        {
            id: 3,
            title: "Bastila",
            image: bastilaImage,
            description: "Une merveille de la cuisine marocaine qui marie le sucré et le salé."
        },
        {
            id: 4,
            title: "Harira",
            image: hariraImage,
            description: "Soupe traditionnelle marocaine riche et réconfortante."
        },
        {
            id: 5,
            title: "Batbout",
            image: batboutImage,
            description: "Pain marocain moelleux cuit à la poêle."
        },
        {
            id: 6,
            title: "Poulet Marocain",
            image: pouletImage,
            description: "Poulet aux épices marocaines et olives."
        }
    ];

    // Charger les recettes au démarrage
    useEffect(() => {
        setRecipes(defaultRecipes);
    }, []);

    // Fonction pour récupérer les recettes
    const fetchRecipes = async (query = '') => {
        setLoading(true);
        try {
            let url = 'http://localhost:8000/api/recipes/';
            if (query) {
                url = `http://localhost:8000/api/search/?query=${encodeURIComponent(query)}`;
            }
            
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                setRecipes(data);
                setSearchStatus(query ? `${data.length} recette(s) trouvée(s) pour "${query}"` : '');
            } else {
                throw new Error('Erreur API');
            }
        } catch (error) {
            console.error('Erreur API:', error);
            // Utiliser les données par défaut en cas d'erreur
            if (query) {
                const filtered = defaultRecipes.filter(recipe => 
                    recipe.title.toLowerCase().includes(query.toLowerCase()) ||
                    recipe.description.toLowerCase().includes(query.toLowerCase())
                );
                setRecipes(filtered);
                setSearchStatus(`${filtered.length} recette(s) trouvée(s) pour "${query}"`);
            } else {
                setRecipes(defaultRecipes);
                setSearchStatus('Serveur non disponible - Recettes par défaut');
            }
        }
        setLoading(false);
    };

    // Recherche par texte
    const handleSearch = () => {
        if (searchQuery.trim()) {
            setSearchStatus(`Recherche en cours pour: "${searchQuery}"`);
            fetchRecipes(searchQuery);
        } else {
            setRecipes(defaultRecipes);
            setSearchStatus('');
        }
    };

    // Recherche par voix
    const handleVoiceSearch = () => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.lang = 'fr-FR';
            recognition.interimResults = false;
            
            recognition.onstart = () => {
                setIsListening(true);
                setSearchStatus('Écoute en cours... Parlez maintenant.');
            };
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setSearchQuery(transcript);
                setSearchStatus('Recherche vocale: ' + transcript);
                fetchRecipes(transcript);
            };
            
            recognition.onerror = (event) => {
                setSearchStatus('Erreur: ' + event.error);
            };
            
            recognition.onend = () => {
                setIsListening(false);
            };
            
            recognition.start();
        } else {
            setSearchStatus('Reconnaissance vocale non supportée');
        }
    };

    // Recherche par image
    const handleImageSearch = () => {
        fileInputRef.current?.click();
    };

    const handleImageChange = async (event) => {
        const file = event.target.files[0];
        if (file) {
            setSearchStatus('Analyse de l\'image...');
            setTimeout(() => {
                setSearchQuery('tajine');
                setSearchStatus('Image analysée - recherche pour "tajine"');
                fetchRecipes('tajine');
            }, 1000);
        }
    };

    // Navigation
    const handleNavClick = (sectionId) => {
        const section = document.querySelector(sectionId);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    // Gestion des erreurs d'images
    const handleImageError = (e) => {
        e.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=250&fit=crop';
        e.target.alt = 'Image non disponible';
    };

    return (
        <div className="chhiwat-dar">
            {/* Hero Section */}
            <section className="hero-section">
                <header>
                    <nav>
                        <a href="#accueil" onClick={(e) => { e.preventDefault(); handleNavClick('.hero-section'); }}>
                            Accueil
                        </a>
                        <a href="#recettes" onClick={(e) => { e.preventDefault(); handleNavClick('#recettes'); }}>
                            Mes Recettes
                        </a>
                        <a href="#apropos" onClick={(e) => { e.preventDefault(); handleNavClick('#apropos'); }}>
                            À Propos
                        </a>
                    </nav>
                </header>

                <div className="title-container">
                    <h1 className="main-title">chhiwatDar</h1>
                    <h2 className="arabic-title">شهيوات الدار</h2>
                    <p className="subtitle">
                        Découvrez l'authenticité de la cuisine marocaine traditionnelle
                    </p>
                </div>
            </section>

            {/* Search Container */}
            <div className="search-container">
                <div className="search-box">
                    <div className="search-input-wrapper">
                        <svg className="search-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                        <input 
                            type="text" 
                            className="search-input" 
                            placeholder="Rechercher une recette marocaine..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </div>
                    <div className="search-actions">
                        <button className={`voice-btn ${isListening ? 'active' : ''}`} onClick={handleVoiceSearch}>
                            <svg className="voice-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="22"></line>
                            </svg>
                        </button>
                        <div className="action-divider"></div>
                        <button className="camera-btn" onClick={handleImageSearch}>
                            <svg className="camera-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <circle cx="9" cy="9" r="2"></circle>
                                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <div className="search-status">{searchStatus}</div>
                <input type="file" ref={fileInputRef} className="image-input" accept="image/*" onChange={handleImageChange} />
            </div>

            {/* Recipes Section */}
            <section className="recipes-section" id="recettes">
                <h2 className="section-title">Les Recettes Marocaines</h2>
                <p className="section-subtitle">
                    Découvrez l'authenticité de la cuisine marocaine traditionnelle
                </p>
                
                {loading ? (
                    <div className="loading">Chargement...</div>
                ) : (
                    <div className="recipes-grid">
                        {recipes.map(recipe => (
                            <div key={recipe.id} className="recipe-card">
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
                        ))}
                    </div>
                )}
            </section>

            {/* Footer */}
            <footer id="apropos">
                <p><strong>chhiwatDar</strong> - Votre guide de la cuisine marocaine authentique</p>
                <p>Préserver et partager les traditions culinaires du Maroc</p>
                <p>&copy; 2024 chhiwatDar - Tous droits réservés</p>
            </footer>
        </div>
    );
};

export default ChhiwatDar;