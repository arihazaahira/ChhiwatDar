import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/ImageResultPage.css';

const ImageResultPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { analysisResult, imagePreview } = location.state || {};

  if (!analysisResult) {
    return (
      <div className="result-page">
        <div className="no-result">
          <h2>Aucun résultat disponible</h2>
          <button onClick={() => navigate('/')}>Retour à l'accueil</button>
        </div>
      </div>
    );
  }

  const { nom_recette, ingredients_visibles } = analysisResult;

  return (
    <div className="result-page">
      <div className="result-container">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Retour
        </button>

        <h1 className="result-title">Analyse de votre image</h1>

        <div className="result-content">
          {/* Image uploadée */}
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Image analysée" />
            </div>
          )}

          {/* Résultats de l'analyse */}
          <div className="analysis-results">
            <div className="result-section">
              <h2>🍽️ Plat détecté</h2>
              <div className="recipe-name">
                {nom_recette}
              </div>
            </div>

            <div className="result-section">
              <h2>🥘 Ingrédients visibles</h2>
              <ul className="ingredients-list">
                {ingredients_visibles && ingredients_visibles.length > 0 ? (
                  ingredients_visibles.map((ingredient, index) => (
                    <li key={index}>{ingredient}</li>
                  ))
                ) : (
                  <li>Aucun ingrédient détecté</li>
                )}
              </ul>
            </div>

            {/* Bouton pour rechercher la recette */}
            <button 
              className="search-recipe-btn"
              onClick={() => navigate('/', { state: { searchQuery: nom_recette } })}
            >
              Rechercher cette recette
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageResultPage;