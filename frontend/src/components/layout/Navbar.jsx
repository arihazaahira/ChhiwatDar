import React from 'react';

const Navbar = ({ onNavClick }) => {
  const handleNavClick = (sectionId) => {
    const section = document.querySelector(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (onNavClick) onNavClick(sectionId);
  };

  return (
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
  );
};

export default Navbar;