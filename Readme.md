# 🍲 ChhiwatDar - شهيوات الدار

Application web de recettes de cuisine marocaine traditionnelle avec recherche intelligente.

🍽️ Description du Projet

Ce projet est un moteur de recherche intelligent dédié aux recettes marocaines, basé sur trois modalités :

Recherche textuelle

Recherche vocale (Speech-to-Text)

Recherche par image

Le système se compose de :

Frontend React + Vite

Backend Django REST

Modules de Machine Learning (indexation, embedding, classification image, STT)

🏗️ 1. Architecture Globale
root/
│
├── backend/         # Serveur Django (API, indexation, ML)
├── frontend/        # Interface utilisateur (React + Vite)
└── README.md
🎨 2. Architecture Frontend (React + Vite)
frontend/
│
├── public/
│
├── src/
│   ├── assets/
│   ├── api/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── styles/
│   ├── App.jsx
│   ├── main.jsx
│   └── router.jsx
│
├── vite.config.js
└── package.json
🔵 2.1 Description des dossiers Frontend
📁 public/

Contient les fichiers statiques disponibles publiquement
(logo, favicon, manifest.json…).

📁 src/assets/

Images, icônes et ressources multimédia localisées côté frontend.
📁 src/api/

Rôle : Centralise tous les appels vers le backend Django
Chaque fichier correspond à une modalité.

textSearchApi.js → recherche textuelle

voiceSearchApi.js → envoi de l’audio / STT

imageSearchApi.js → upload d’images, extraction features

recipesApi.js → récupération des recettes (listing, détails)
📁 src/components/

Contient tous les composants réutilisables.

📁 search/

TextSearchBar.jsx → input recherche textuelle

VoiceRecorder.jsx → enregistrement audio

ImageUploader.jsx → upload + preview

SearchTabs.jsx → sélection modalité
📁 recipes/

RecipeCard.jsx → carte d'une recette

RecipeList.jsx → liste des recettes

📁 layout/

Navbar.jsx

Footer.jsx
📁 src/hooks/

Hooks personnalisés pour isoler la logique.

useTextSearch.js → gère la recherche textuelle

useVoiceSearch.js → traite l’audio + call API

useImageSearch.js → gère upload + features image
📁 src/pages/

Pages principales de l’application.

Home.jsx → choix modalité + formulaire

SearchResults.jsx → résultats renvoyés par le backend

RecipeDetails.jsx → détails d’une recette
📁 src/services/

Contient la logique "helper", non liée au backend.

audioService.js → conversion audio, nettoyage

imageService.js → validation/redimensionnement image

textService.js → normalisation du texte

📁 src/styles/

Fichiers CSS globaux + styles par page.
Architecture Backend (Django)
backend/
│
├── backend/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── data/
│   └── recipes.json
│
├── search_api/
│   ├── __pycache__/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
│   │
│   ├── indexing/
│   ├── text_search/
│   ├── image_search/
│   └── voice_search/
│
└── manage.py
📁 indexing/

→ Module central d’indexation
📁 text_search/

→ Recherche textuelle classique
📁 voice_search/

→ Recherche vocale + Speech-To-Text
📁 image_search/

→ Recherche basée sur l’analyse d’image






