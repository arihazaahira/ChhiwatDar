import React, { useState } from 'react';
import "../styles/ChhiwatDar.css";

// Components
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import TextSearchBar from '../components/search/TextSearchBar';
import VoiceRecorder from '../components/search/VoiceRecorder';
import ImageUploader from '../components/search/ImageUploader';
import RecipeList from '../components/recipes/RecipeList';

// Hooks
import { useRecipes } from '../hooks/useRecipes';

const Home = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchStatus, setSearchStatus] = useState('');
    
    const { recipes, loading, fetchRecipes } = useRecipes();

    // Recherche par texte
    const handleTextSearch = () => {
        if (searchQuery.trim()) {
            setSearchStatus(`Recherche en cours pour: "${searchQuery}"`);
            fetchRecipes(searchQuery);
        } else {
            fetchRecipes();
            setSearchStatus('');
        }
    };

    // Recherche par voix
    const handleVoiceSearch = (transcript) => {
        setSearchQuery(transcript);
        setSearchStatus('Recherche vocale: ' + transcript);
        fetchRecipes(transcript);
    };

    // Recherche par image
    const handleImageSearch = (query) => {
        setSearchQuery(query);
        fetchRecipes(query);
    };

    const handleImageAnalysis = (status) => {
        setSearchStatus(status);
    };

    return (
        <div className="chhiwat-dar">
            {/* Hero Section */}
            <section className="hero-section">
                <Navbar />
                
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
                    <TextSearchBar 
                        searchQuery={searchQuery}
                        setSearchQuery={setSearchQuery}
                        onSearch={handleTextSearch}
                    />
                    <div className="search-actions">
                        <VoiceRecorder onTranscript={handleVoiceSearch} />
                        <div className="action-divider"></div>
                        <ImageUploader 
                            onImageSelect={handleImageSearch}
                            onImageAnalysis={handleImageAnalysis}
                        />
                    </div>
                </div>
                <div className="search-status">{searchStatus}</div>
            </div>

            {/* Recipes Section */}
            <section className="recipes-section" id="recettes">
                <h2 className="section-title">Les Recettes Marocaines</h2>
                <p className="section-subtitle">
                    Découvrez l'authenticité de la cuisine marocaine traditionnelle
                </p>
                
                <RecipeList recipes={recipes} loading={loading} />
            </section>

            <Footer />
        </div>
    );
};

export default Home;