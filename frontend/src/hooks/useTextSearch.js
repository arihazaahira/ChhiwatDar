import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const useTextSearch = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const search = async (query) => {
        if (!query.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/text-search/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: query })
            });

            const data = await response.json();

            if (data.success && data.matching_recipes) {
                // ✅ Naviguer vers la page TextResultPage
                navigate('/text-results', {
                    state: {
                        matching_recipes: data.matching_recipes,
                        original_text: query,
                        dish_name_english: data.dish_name_english,
                        transcription: data.transcription,
                        translation: data.translation
                    }
                });
            } else {
                setError('❌ Aucune recette trouvée');
            }
        } catch (err) {
            console.error('Erreur lors de la recherche :', err);
            setError('❌ Erreur de connexion');
        } finally {
            setLoading(false);
        }
    };

    return { search, loading, error };
};
