// Navbar.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    const navigate = useNavigate();

    const scrollToSection = (sectionId) => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <nav className="navbar">
            <div className="nav-container">
                <div className="nav-left">
                    <span 
                        className="nav-logo"
                        onClick={() => navigate('/')}
                    >
                     
                    </span>
                </div>

                <div className="nav-center">
                    <a 
                        className="nav-link" 
                        onClick={() => scrollToSection('recettes')}
                    >
                        Recettes
                    </a>
                    <a 
                        className="nav-link" 
                        onClick={() => scrollToSection('about')}
                    >
                        À Propos
                    </a>
                    <a 
                        className="nav-link" 
                        onClick={() => scrollToSection('contact')}
                    >
                        Contact
                    </a>
                    <a 
                        className="nav-link" 
                        onClick={() => navigate('/create-recipe')}
                    >
                        Créer ma recette
                    </a>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;