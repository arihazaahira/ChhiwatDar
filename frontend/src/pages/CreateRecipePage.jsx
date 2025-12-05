// src/pages/CreateRecipe.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/CreateRecipe.css";

export default function CreateRecipe() {
    const navigate = useNavigate();
    
    // États du formulaire
    const [recipeName, setRecipeName] = useState("");
    const [description, setDescription] = useState("");
    const [authorName, setAuthorName] = useState("");
    const [ingredients, setIngredients] = useState([{ name: "", quantity: "" }]);
    const [steps, setSteps] = useState([""]);
    const [images, setImages] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Gestion des ingrédients
    const handleIngredientChange = (index, field, value) => {
        const newIngredients = [...ingredients];
        newIngredients[index][field] = value;
        setIngredients(newIngredients);
    };

    const addIngredient = () => {
        setIngredients([...ingredients, { name: "", quantity: "" }]);
    };

    const removeIngredient = (index) => {
        if (ingredients.length > 1) {
            const newIngredients = ingredients.filter((_, i) => i !== index);
            setIngredients(newIngredients);
        }
    };

    // Gestion des étapes
    const handleStepChange = (index, value) => {
        const newSteps = [...steps];
        newSteps[index] = value;
        setSteps(newSteps);
    };

    const addStep = () => {
        setSteps([...steps, ""]);
    };

    const removeStep = (index) => {
        if (steps.length > 1) {
            const newSteps = steps.filter((_, i) => i !== index);
            setSteps(newSteps);
        }
    };

    // Gestion des images
    const handleImageChange = (e) => {
        const files = Array.from(e.target.files);
        const newImages = files.map(file => ({
            file,
            preview: URL.createObjectURL(file)
        }));
        setImages([...images, ...newImages]);
    };

    const removeImage = (index) => {
        const newImages = images.filter((_, i) => i !== index);
        setImages(newImages);
    };

    // Soumission du formulaire
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        
        try {
            console.log("📤 Envoi de la recette au serveur...");
            
            // Préparer les données pour le backend
            const formData = new FormData();
            
            // Champs obligatoires
            formData.append('title', recipeName);
            formData.append('description', description);
            formData.append('user_name', authorName || 'Chef Anonyme');
            
            // Formater les ingrédients pour le backend
            const ingredientsList = ingredients
                .filter(ing => ing.name.trim() !== '')
                .map(ing => `${ing.quantity} ${ing.name}`);
            formData.append('ingredients', JSON.stringify(ingredientsList));
            
            console.log("🥘 Ingrédients:", ingredientsList);
            
            // Formater les étapes pour le backend
            const stepsList = steps.filter(step => step.trim() !== '');
            formData.append('steps', JSON.stringify(stepsList));
            
            console.log("👨‍🍳 Étapes:", stepsList);
            
            // Ajouter la première image (si disponible)
            if (images.length > 0) {
                formData.append('image', images[0].file);
                console.log("📷 Image ajoutée:", images[0].file.name);
            }
            
            // Envoyer au backend
            const response = await fetch('http://localhost:8000/api/recipes/create/', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            console.log("📥 Réponse du serveur:", result);
            
            if (result.success) {
                alert("🎉 Recette créée avec succès !");
                console.log("✅ Recette enregistrée dans user_recipes.json");
                
                // Rediriger vers la page d'accueil
                navigate('/');
            } else {
                alert("❌ Erreur lors de la création : " + (result.error || "Veuillez réessayer"));
                console.error("Erreur:", result.error);
            }
        } catch (error) {
            console.error('❌ Erreur de connexion:', error);
            alert("❌ Erreur de connexion au serveur. Vérifiez que le backend est lancé.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="create-recipe-page">
            <div className="create-recipe-container">
                <button 
                    className="recipe-back-button"
                    onClick={() => navigate('/')}
                >
                    ← Retour à l'accueil
                </button>

                <div className="recipe-page-header">
                    <h1 className="page-title">Créer Votre Recette</h1>
                    <p className="page-subtitle">
                        Partagez votre création culinaire avec la communauté شهيوات الدار
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="create-recipe-form">
                    
                    {/* ========== INFORMATIONS DE BASE ========== */}
                    <div className="form-section">
                        <div className="section-header">
                            <div className="section-icon">📝</div>
                            <h2 className="section-title">Informations de Base</h2>
                        </div>
                        
                        <div className="form-group">
                            <label>Nom de la recette *</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="ex: Tajine d'agneau aux pruneaux"
                                value={recipeName}
                                onChange={(e) => setRecipeName(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Votre nom (optionnel)</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="ex: Chef Hassan"
                                value={authorName}
                                onChange={(e) => setAuthorName(e.target.value)}
                            />
                            <small style={{ color: '#666', fontSize: '0.9rem' }}>
                                Laissez vide pour rester anonyme
                            </small>
                        </div>

                        <div className="form-group">
                            <label>Description *</label>
                            <textarea
                                className="form-input form-textarea"
                                placeholder="Décrivez votre recette..."
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows="4"
                                required
                            />
                        </div>
                    </div>

                    {/* ========== INGRÉDIENTS ========== */}
                    <div className="form-section">
                        <div className="section-header">
                            <div className="section-icon">🥘</div>
                            <h2 className="section-title">Ingrédients</h2>
                        </div>
                        
                        <div className="ingredients-container">
                            {ingredients.map((ing, index) => (
                                <div key={index} className="ingredient-row">
                                    <input
                                        type="text"
                                        className="form-input"
                                        placeholder="Quantité (ex: 200g, 1 tasse)"
                                        value={ing.quantity}
                                        onChange={(e) => handleIngredientChange(index, "quantity", e.target.value)}
                                        required
                                        style={{ flex: '0 0 150px' }}
                                    />
                                    <input
                                        type="text"
                                        className="form-input"
                                        placeholder="Nom de l'ingrédient"
                                        value={ing.name}
                                        onChange={(e) => handleIngredientChange(index, "name", e.target.value)}
                                        required
                                        style={{ flex: '1' }}
                                    />
                                    {ingredients.length > 1 && (
                                        <button
                                            type="button"
                                            className="remove-btn"
                                            onClick={() => removeIngredient(index)}
                                            style={{
                                                padding: '8px 12px',
                                                background: '#e74c3c',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            ✕
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                        
                        <button 
                            type="button" 
                            className="add-button"
                            onClick={addIngredient}
                        >
                            + Ajouter un ingrédient
                        </button>
                    </div>

                    {/* ========== ÉTAPES DE PRÉPARATION ========== */}
                    <div className="form-section">
                        <div className="section-header">
                            <div className="section-icon">👨‍🍳</div>
                            <h2 className="section-title">Étapes de Préparation</h2>
                        </div>
                        
                        <div className="steps-container">
                            {steps.map((step, index) => (
                                <div key={index} className="step-row">
                                    <div className="step-number">{index + 1}</div>
                                    <textarea
                                        className="form-input form-textarea step-textarea"
                                        placeholder={`Décrivez l'étape ${index + 1}...`}
                                        value={step}
                                        onChange={(e) => handleStepChange(index, e.target.value)}
                                        required
                                        style={{ flex: '1' }}
                                    />
                                    {steps.length > 1 && (
                                        <button
                                            type="button"
                                            className="remove-btn"
                                            onClick={() => removeStep(index)}
                                            style={{
                                                padding: '8px 12px',
                                                background: '#e74c3c',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                alignSelf: 'flex-start'
                                            }}
                                        >
                                            ✕
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                        
                        <button 
                            type="button" 
                            className="add-button"
                            onClick={addStep}
                        >
                            + Ajouter une étape
                        </button>
                    </div>

                    {/* ========== IMAGES ========== */}
                    <div className="form-section">
                        <div className="section-header">
                            <div className="section-icon">📷</div>
                            <h2 className="section-title">Photos de Votre Recette</h2>
                        </div>
                        
                        <div className="image-upload-section">
                            <label className="upload-label">
                                <input
                                    type="file"
                                    multiple
                                    onChange={handleImageChange}
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                />
                                <div className="upload-icon">📸</div>
                                <div className="upload-text">Ajouter des photos</div>
                                <div className="upload-hint">Glissez-déposez ou cliquez pour sélectionner</div>
                            </label>
                        </div>

                        {images.length > 0 && (
                            <div className="images-preview">
                                {images.map((image, index) => (
                                    <div key={index} className="image-preview-item">
                                        <img src={image.preview} alt={`Preview ${index}`} />
                                        <button
                                            type="button"
                                            className="remove-image"
                                            onClick={() => removeImage(index)}
                                        >
                                            ✕
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* ========== BOUTON DE SOUMISSION ========== */}
                    <button 
                        type="submit" 
                        className="submit-button"
                        disabled={isSubmitting}
                        style={{
                            opacity: isSubmitting ? 0.7 : 1,
                            cursor: isSubmitting ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {isSubmitting ? '📤 Publication en cours...' : '✨ Publier la Recette'}
                    </button>
                </form>
            </div>
        </div>
    );
}