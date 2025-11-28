import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { recipesApi } from '../api/recipesApi';
import { getRecipeImage } from '../assets/images';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import '../styles/ChhiwatDar.css';

const DetailsRecipe = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openSections, setOpenSections] = useState({
    ingredients: true,
    preparation: true,
    conseils: true
  });

  // Fonction pour toggle les sections
  const toggleSection = (section) => {
    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Fonction pour obtenir l'image correcte
  const getImageForRecipe = (recipeData) => {
    if (!recipeData) return '';
    
    if (recipeData.image && recipeData.image.startsWith('http')) {
      return recipeData.image;
    }
    
    if (recipeData.image && recipeData.image.includes('/assets/')) {
      return getRecipeImage(recipeData.id);
    }
    
    return getRecipeImage(recipeData.id);
  };

  useEffect(() => {
    const loadRecipe = async () => {
      try {
        const apiData = await recipesApi.getRecipeDetails(id);
        
        const recipeWithImage = {
          ...apiData,
          image: getImageForRecipe(apiData)
        };
        
        console.log("📦 DONNÉES API CHARGÉES:", recipeWithImage);
        console.log("🔢 NOMBRE D'INGRÉDIENTS:", recipeWithImage.ingredients?.length);
        console.log("📝 LONGUEUR DES INSTRUCTIONS:", recipeWithImage.instructions?.length);
        
        setRecipe(recipeWithImage);
      } catch (error) {
        console.log("❌ ERREUR API - Utilisation des données de démonstration");
        
        const demoRecipes = {
          1: {
            id: 1,
            title: "Tajine de Poulet aux Citrons Confits",
            description: "Un plat marocain emblématique cuit lentement avec des citrons confits et des olives, révélant des saveurs complexes et une viande tendre qui fond dans la bouche.",
            image: getRecipeImage(1),
            temps_cuisson: "90 minutes",
            difficulte: "Moyenne",
            personnes: "4-6 personnes",
            ingredients: [
              "1 poulet entier coupé en morceaux",
              "2 citrons confits coupés en quartiers", 
              "100g d'olives vertes dénoyautées",
              "2 oignons finement émincés",
              "4 gousses d'ail pressées",
              "1 cuillère à café de gingembre frais râpé",
              "1 pincée de safran",
              "1 bouquet de coriandre fraîche",
              "1 bouquet de persil frais",
              "4 cuillères à soupe d'huile d'olive",
              "Sel et poivre noir au goût"
            ],
            instructions: `1. PRÉPARATION DES INGRÉDIENTS
• Couper le poulet en 8 morceaux réguliers
• Émincer finement les oignons en lamelles  
• Presser l'ail frais
• Couper les citrons confits en quartiers
• Dénoyauter les olives vertes

2. DÉMARRAGE DE LA CUISSON
• Dans un tajine traditionnel, faire chauffer l'huile d'olive à feu moyen
• Faire revenir les oignons émincés jusqu'à ce qu'ils deviennent translucides
• Ajouter l'ail pressé et poursuivre la cuisson 2 minutes
• Déposer les morceaux de poulet et les faire dorer sur toutes les faces

3. ASSAISONNEMENT ET ÉPICES
• Saupoudrer le gingembre frais râpé sur le poulet
• Ajouter la pincée de safran pour la couleur et l'arôme
• Saler et poivrer selon votre goût
• Bien mélanger pour enrober uniformément le poulet

4. AJOUT DES AROMATES
• Répartir les quartiers de citrons confits entre les morceaux de poulet
• Ajouter les olives vertes dénoyautées
• Verser délicatement de l'eau chaude jusqu'à mi-hauteur des ingrédients

5. MÉTHODE DE MIJOTAGE TRADITIONNELLE
• Couvrir le tajine avec son couvercle conique
• Baisser le feu au minimum et laisser mijoter pendant 1 heure 15 minutes
• Résister à l'envie de soulever le couvercle pendant la cuisson
• La vapeur doit circuler naturellement dans le tajine

6. FINALISATION ET SERVICE
• Vérifier la cuisson du poulet (la chair doit se détacher facilement)
• Rectifier l'assaisonnement si nécessaire
• Parsemer généreusement de coriandre et persil frais ciselés
• Servir immédiatement dans le tajine pour préserver la chaleur
• Accompagner de pain marocain pour tremper dans le jus`,
            conseils: "Pour un tajine parfait, laissez-le mijoter à feu très doux et ne soulevez pas le couvercle pendant la cuisson. Les citrons confits apportent une saveur unique - ne les remplacez pas par des citrons frais."
          },
          2: {
            id: 2,
            title: "Couscous aux Légumes",
            description: "Le plat traditionnel du vendredi, une symphonie de semoule fine accompagnée de légumes de saison et d'un bouillon parfumé aux épices marocaines.",
            image: getRecipeImage(2),
            temps_cuisson: "120 minutes", 
            difficulte: "Facile",
            personnes: "6-8 personnes",
            ingredients: [
              "500g de semoule moyenne pour couscous",
              "4 carottes pelées et coupées en tronçons",
              "2 courgettes coupées en gros morceaux", 
              "4 navets pelés et coupés en quartiers",
              "2 tomates pelées et coupées en quartiers",
              "200g de pois chiches trempés overnight",
              "1 oignon finement émincé",
              "2 cuillères à soupe d'huile d'olive",
              "1 cuillère à café de gingembre",
              "1 cuillère à café de curcuma", 
              "1 pincée de safran",
              "Sel et poivre au goût",
              "3 litres d'eau chaude"
            ],
            instructions: `ÉTAPE 1 : PRÉPARATION DE LA SEMOULE
• Verser 500g de semoule moyenne dans un grand plat en terre cuite
• Humidifier progressivement avec 250ml d'eau légèrement salée  
• Travailler la semoule du bout des doigts pour séparer les grains
• Laisser reposer 15 minutes pour absorption

ÉTAPE 2 : PRÉPARATION DU BOUILLON AROMATIQUE  
• Dans le bas du couscoussier, faire chauffer l'huile d'olive
• Faire revenir l'oignon émincé jusqu'à coloration dorée
• Ajouter les tomates pelées et coupées en morceaux
• Incorporer les épices : gingembre, curcuma, safran
• Laisser mijoter 5 minutes pour développer les arômes

ÉTAPE 3 : CUISSON DES LÉGUMES RACINES
• Ajouter les carottes et navets coupés en gros tronçons
• Incorporer les pois chiches préalablement trempés 12 heures
• Couvrir de 3 litres d'eau chaude pour préserver les nutriments  
• Porter à ébullition puis baisser immédiatement le feu

ÉTAPE 4 : PREMIÈRE CUISSON À LA VAPEUR
• Placer la semoule humidifiée dans le panier supérieur
• Cuire à la vapeur pendant 45 minutes sans remuer
• La vapeur du bouillon parfume naturellement la semoule
• Retirer délicatement la semoule du couscoussier

ÉTAPE 5 : TRAVAIL DE LA SEMOULE
• Étaler la semoule cuite sur un grand plateau
• L'arroser uniformément d'eau froide (environ 200ml)
• Séparer les grains à la fourchette en soulevant délicatement
• Éliminer les éventuels grumeaux pour une texture parfaite

ÉTAPE 6 : DEUXIÈME CUISSON ET FINALISATION
• Ajouter les courgettes dans le bouillon en cours de cuisson
• Remettre la semoule travaillée dans le panier vapeur
• Poursuivre la cuisson 30 minutes supplémentaires
• Vérifier la tendreté des légumes et rectifier l'assaisonnement

ÉTAPE 7 : SERVICE TRADITIONNEL
• Dresser la semoule en dôme majestueux dans un plat de service
• Disposer harmonieusement les légumes tout autour
• Servir le bouillon aromatique à part dans une soupière
• Chacun peut ainsi doser selon ses préférences personnelles`,
            conseils: "Pour une semoule parfaite, faites-la cuire à la vapeur trois fois en la travaillant entre chaque cuisson. La texture doit être légère et les grains bien séparés."
          },
          3: {
            id: 3,
            title: "Bastila au Poulet",
            description: "Feuilleté sucré-salé typique de la cuisine marocaine, alliant la finesse des feuilles de brick à la richesse des amandes et des épices.",
            image: getRecipeImage(3),
            temps_cuisson: "60 minutes",
            difficulte: "Difficile",
            personnes: "6-8 personnes",
            ingredients: [
              "1 poulet cuit et effiloché",
              "200g d'amandes effilées",
              "8 œufs battus",
              "2 oignons finement émincés",
              "100g de sucre",
              "1 cuillère à café de cannelle",
              "10 feuilles de brick",
              "100g de beurre fondu",
              "1 bouquet de coriandre",
              "1 cuillère à café de gingembre",
              "1 pincée de safran",
              "Sel et poivre au goût"
            ],
            instructions: `PRÉPARATION DE LA GARNITURE
• Faire revenir les oignons dans l'huile d'olive
• Ajouter le poulet effiloché et les épices
• Incorporer les œufs battus et cuire jusqu'à consistance crémeuse
• Réserver la préparation

PRÉPARATION DES AMANDES
• Torréfier les amandes à sec dans une poêle
• Les mixer grossièrement avec le sucre et la cannelle
• Réserver le mélange amandes-sucre

MONTAGE DE LA BASTILA
• Beurrer généreusement un moule à tarte
• Superposer 5 feuilles de brick en les badigeonnant de beurre
• Étaler la moitié de la garniture au poulet
• Saupoudrer du mélange amandes-sucre
• Ajouter le reste de garniture au poulet
• Recouvrir avec les 5 feuilles de brick restantes
• Bien soulever les bords pour formar un paquet

CUISSON
• Badigeonner le dessus de beurre fondu
• Cuire au four à 180°C pendant 30 minutes
• Retourner délicatement la bastila
• Poursuivre la cuisson 10 minutes
• La surface doit être dorée et croustillante

SERVICE
• Saupoudrer généreusement de sucre glace et de cannelle
• Découper en parts comme un gâteau
• Servir chaud pour apprécier le contraste sucré-salé`,
            conseils: "Pour une bastila parfaite, travaillez rapidement les feuilles de brick pour qu'elles ne sèchent pas. Le contraste entre le salé du poulet et le sucré des amandes est essentiel."
          }
        };

        const demoRecipe = demoRecipes[id] || demoRecipes[1];
        
        // LOGS DE DEBUG DÉTAILLÉS
        console.log("🎯 RECETTE DÉMO CHARGÉE:", demoRecipe.title);
        console.log("📊 INGRÉDIENTS:", demoRecipe.ingredients);
        console.log("🔢 NOMBRE D'INGRÉDIENTS:", demoRecipe.ingredients?.length);
        console.log("📏 LONGUEUR INSTRUCTIONS:", demoRecipe.instructions?.length);
        console.log("📄 INSTRUCTIONS COMPLÈTES:");
        console.log(demoRecipe.instructions);
        
        setRecipe(demoRecipe);
      }
      setLoading(false);
    };

    loadRecipe();
  }, [id]);

  // Gestionnaire d'erreur d'image
  const handleImageError = (e) => {
    console.log("❌ ERREUR IMAGE - Utilisation fallback");
    e.target.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&h=600&fit=crop';
    e.target.alt = 'Image de recette marocaine';
  };

  // Fonction pour formater les instructions - AVEC LOGS
  const formatInstructions = (text) => {
    console.log("🔧 FORMAT INSTRUCTIONS APPELÉ");
    
    if (!text) {
      console.log("❌ AUCUN TEXTE D'INSTRUCTIONS");
      return <div className="no-instructions">Aucune instruction disponible</div>;
    }
    
    console.log("✅ TEXTE REÇU:", text);
    
    const lines = text.split('\n').filter(line => line.trim() !== '');
    console.log("📝 LIGNES DÉTECTÉES:", lines.length);
    
    const result = lines.map((line, index) => {
      const trimmedLine = line.trim();
      
      // Titres des sections
      if (/^\d+\.|^ÉTAPE\s+\d+|^PRÉPARATION|^MONTAGE|^CUISSON|^SERVICE/i.test(trimmedLine)) {
        console.log("🏷️ TITRE DÉTECTÉ:", trimmedLine);
        return (
          <div key={index} className="instruction-title">
            {trimmedLine}
          </div>
        );
      }
      
      // Étapes avec bullet points
      if (/^[•\-]/.test(trimmedLine)) {
        return (
          <div key={index} className="instruction-step">
            <span className="step-bullet">•</span>
            <span className="step-text">{trimmedLine.replace(/^[•\-]\s*/, '')}</span>
          </div>
        );
      }
      
      // Texte normal
      return (
        <div key={index} className="instruction-text">
          {trimmedLine}
        </div>
      );
    });
    
    console.log("🎨 ÉLÉMENTS GÉNÉRÉS:", result.length);
    return result;
  };

  if (loading) {
    return (
      <div className="chhiwat-dar">
        <Navbar />
        <div className="loading">
          <div className="loading-spinner"></div>
          Chargement de la recette...
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="chhiwat-dar">
        <Navbar />
        <div className="no-results">
          <h3>Recette non trouvée</h3>
          <button onClick={() => navigate('/')} className="luxury-back-button">
            <span className="back-arrow">←</span>
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  console.log("🎬 RENDU DU COMPOSANT - Recette:", recipe.title);

  return (
    <div className="chhiwat-dar">
      {/* Hero Section Luxueuse */}
      <section className="hero-section recipe-detail-hero">
        <div className="hero-overlay"></div>
        <Navbar />
        
        <div className="recipe-hero-content">
          <button onClick={() => navigate('/')} className="luxury-back-button">
            <span className="back-arrow">←</span>
            Retour aux recettes
          </button>
          
          <div className="recipe-hero-info">
            <div className="recipe-badge">{recipe.difficulte}</div>
            <h1 className="recipe-main-title">{recipe.title}</h1>
            <p className="recipe-hero-description">{recipe.description}</p>
            
            <div className="recipe-meta-grid">
              <div className="meta-item">
                <span className="meta-icon">⏱️</span>
                <div>
                  <div className="meta-label">Temps de cuisson</div>
                  <div className="meta-value">{recipe.temps_cuisson}</div>
                </div>
              </div>
              
              <div className="meta-item">
                <span className="meta-icon">👥</span>
                <div>
                  <div className="meta-label">Personnes</div>
                  <div className="meta-value">{recipe.personnes}</div>
                </div>
              </div>
              
              <div className="meta-item">
                <span className="meta-icon">⚡</span>
                <div>
                  <div className="meta-label">Difficulté</div>
                  <div className="meta-value">{recipe.difficulte}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section Détails */}
      <section className="recipe-detail-section">
        <div className="recipe-detail-container">
          {/* Colonne Image */}
          <div className="recipe-image-column">
            <div className="recipe-image-wrapper">
              <img 
                src={recipe.image} 
                alt={recipe.title}
                className="recipe-detail-image"
                onError={handleImageError}
              />
              <div className="image-overlay"></div>
            </div>
          </div>

          {/* Colonne Contenu */}
          <div className="recipe-content-column">
            {/* Ingrédients - Section Accordéon */}
            <div className="detail-card">
              <div 
                className="card-header accordion-header"
                onClick={() => toggleSection('ingredients')}
                style={{cursor: 'pointer'}}
              >
                <h2 className="card-title">
                  <span className="title-icon">🥘</span>
                  Ingrédients
                  <span className="accordion-arrow">
                    {openSections.ingredients ? '▼' : '▶'}
                  </span>
                </h2>
                <div className="card-divider"></div>
              </div>
              
              {openSections.ingredients && (
                <div className="ingredients-list" style={{ maxHeight: 'none', overflow: 'visible' }}>
                  {recipe.ingredients && recipe.ingredients.map((ingredient, index) => (
                    <div key={index} className="ingredient-item">
                      <span className="ingredient-checkbox"></span>
                      <span className="ingredient-text">{ingredient}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Préparation - Section Accordéon */}
            <div className="detail-card">
              <div 
                className="card-header accordion-header"
                onClick={() => toggleSection('preparation')}
                style={{cursor: 'pointer'}}
              >
                <h2 className="card-title">
                  <span className="title-icon">👨‍🍳</span>
                  Préparation
                  <span className="accordion-arrow">
                    {openSections.preparation ? '▼' : '▶'}
                  </span>
                </h2>
                <div className="card-divider"></div>
              </div>
              
              {openSections.preparation && (
                <div className="instructions-container" style={{ 
                  maxHeight: 'none', 
                  overflow: 'visible',
                  height: 'auto'
                }}>
                  {recipe.instructions ? (
                    <div className="instructions-content" style={{ 
                      maxHeight: 'none', 
                      overflow: 'visible',
                      height: 'auto'
                    }}>
                      {formatInstructions(recipe.instructions)}
                    </div>
                  ) : (
                    <div className="no-instructions">
                      <p>Aucune instruction de préparation disponible pour cette recette.</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Conseils du Chef - Section Accordéon */}
            {recipe.conseils && (
              <div className="detail-card chef-tips">
                <div 
                  className="card-header accordion-header"
                  onClick={() => toggleSection('conseils')}
                  style={{cursor: 'pointer'}}
                >
                  <h2 className="card-title">
                    <span className="title-icon">💎</span>
                    Conseils du Chef
                    <span className="accordion-arrow">
                      {openSections.conseils ? '▼' : '▶'}
                    </span>
                  </h2>
                  <div className="card-divider"></div>
                </div>
                
                {openSections.conseils && (
                  <div className="tips-content" style={{ maxHeight: 'none', overflow: 'visible' }}>
                    <p>{recipe.conseils}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default DetailsRecipe;