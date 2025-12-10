import React, { useState } from 'react';
import "../styles/ChhiwatDar.css";

import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import TextSearchBar from '../components/search/TextSearchBar';
import VoiceRecorder from '../components/search/VoiceRecorder';
import ImageUploader from '../components/search/ImageUploader';
import RecipeList from '../components/recipes/RecipeList';

import { useRecipes } from '../hooks/useRecipes';
import { useTextSearch } from '../hooks/useTextSearch';

const Home = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchStatus, setSearchStatus] = useState('');
    
    const { recipes, loading, fetchRecipes } = useRecipes();
    const { search, loading: textLoading, error: searchError } = useTextSearch();

    // Recherche texte
    const handleTextSearch = async () => {
        if (!searchQuery.trim()) return;

        setSearchStatus(`🔍 Analyse: "${searchQuery}"...`);
        await search(searchQuery); // hook gère la navigation vers /text-results
    };

    // Recherche vocale
    const handleVoiceSearch = (transcript) => {
        setSearchQuery(transcript);
        setSearchStatus('🎤 Recherche vocale: ' + transcript);
        fetchRecipes(transcript);
    };

    // Recherche image
    const handleImageSearch = (query) => {
        setSearchQuery(query);
        fetchRecipes(query);
    };

    const handleImageAnalysis = (status) => {
        setSearchStatus(status);
    };

    return (
        <div className="chhiwat-dar">
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

            <div className="search-container">
                <div className="search-box">
                    <TextSearchBar 
                        searchQuery={searchQuery}
                        setSearchQuery={setSearchQuery}
                        onSearch={handleTextSearch} // <-- hook connecté ici
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

            <section className="recipes-section" id="recettes">
                <div className="recipes-header">
                    <h2 className="section-title">Les Recettes Marocaines</h2>
                    <p className="section-subtitle">
                        Éveillez vos sens aux saveurs de la terre marocaine 
                    </p>
                </div>
                
                <RecipeList recipes={recipes} loading={loading} />
            </section>

            <Footer />
        </div>
    );
};

export default Home;
