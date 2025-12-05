# 🍲 ChhiwatDar - شهيوات الدار

Application web de recettes de cuisine marocaine traditionnelle avec recherche intelligente.

---

## 🍽️ Description du Projet

Ce projet est un moteur de recherche intelligent dédié aux recettes marocaines, basé sur trois modalités :
- Recherche textuelle
- Recherche vocale (Speech-to-Text)
- Recherche par image

Le système se compose de :
- Frontend React + Vite
- Backend Django REST
- Modules de Machine Learning (indexation, embedding, classification image, STT)

---

## 🏗️ Architecture Globale

```
root/
│
├── backend/         # Serveur Django (API, indexation, ML)
├── frontend/        # Interface utilisateur (React + Vite)
└── README.md
```

---

## 🎨 Architecture Frontend (React + Vite)

```
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
```

### 🔵 Description des dossiers Frontend

#### 📁 public/
Contient les fichiers statiques disponibles publiquement (logo, favicon, manifest.json…).

#### 📁 src/assets/
Images, icônes et ressources multimédia localisées côté frontend.

#### 📁 src/api/
**Rôle :** Centralise tous les appels vers le backend Django. Chaque fichier correspond à une modalité.

- `textSearchApi.js` → recherche textuelle
- `voiceSearchApi.js` → envoi de l'audio / STT
- `imageSearchApi.js` → upload d'images, extraction features
- `recipesApi.js` → récupération des recettes (listing, détails)

#### 📁 src/components/
Contient tous les composants réutilisables.

**📁 search/**
- `TextSearchBar.jsx` → input recherche textuelle
- `VoiceRecorder.jsx` → enregistrement audio
- `ImageUploader.jsx` → upload + preview
- `SearchTabs.jsx` → sélection modalité

**📁 recipes/**
- `RecipeCard.jsx` → carte d'une recette
- `RecipeList.jsx` → liste des recettes

**📁 layout/**
- `Navbar.jsx`
- `Footer.jsx`

#### 📁 src/hooks/
Hooks personnalisés pour isoler la logique.

- `useTextSearch.js` → gère la recherche textuelle
- `useVoiceSearch.js` → traite l'audio + call API
- `useImageSearch.js` → gère upload + features image

#### 📁 src/pages/
Pages principales de l'application.

- `Home.jsx` → choix modalité + formulaire
- `SearchResults.jsx` → résultats renvoyés par le backend
- `RecipeDetails.jsx` → détails d'une recette

#### 📁 src/services/
Contient la logique "helper", non liée au backend.

- `audioService.js` → conversion audio, nettoyage
- `imageService.js` → validation/redimensionnement image
- `textService.js` → normalisation du texte

#### 📁 src/styles/
Fichiers CSS globaux + styles par page.

---

## ⚙️ Architecture Backend (Django)

```
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
```

### 🔧 Description des modules Backend

#### 📁 indexing/
**Module central d'indexation**

#### 📁 text_search/
**Recherche textuelle classique**

#### 📁 voice_search/
**Recherche vocale + Speech-To-Text**

#### 📁 image_search/
**Recherche basée sur l'analyse d'image**

---

## 🚀 Installation

### Prérequis
- Node.js
- Python
- pip et virtualenv

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---



**Fait avec ❤️ pour préserver la richesse de la cuisine marocaine**


# 📖 Documentation API - Transcription Audio Darija/Anglais (Gemini AI)

    **voice_search/**
    ***Recherche vocale + Speech-To-Text***

## 🇲🇦 API Intelligente Multi-Langues

Cette API utilise **Google Gemini AI** pour transcrire automatiquement l'audio en détectant la langue (Darija marocain ou Anglais) et fournit une traduction en anglais si nécessaire.

---

## 🔒 Confidentialité

**⚠️ AUCUN FICHIER AUDIO N'EST SAUVEGARDÉ**

| Garantie                   | Description                                         |
|----------------------------|-----------------------------------------------------|
| ✅ Traitement temporaire   | Fichiers traités en mémoire uniquement              |
| ✅ Suppression immédiate   | Fichiers supprimés après transcription              |
| ✅ Aucune base de données  | Aucun stockage permanent                            |
| ✅ Nettoyage Gemini        | Fichiers supprimés de l'API Gemini après traitement |

---

## 🌐 Endpoint

| Propriété        | Valeur                                                      |
|------------------|-------------------------------------------------------------|
| **URL**          | `http://localhost:8000/api/speachfrang/default/transcribe/` |
| **Méthode**      | `POST`                                                      |
| **Content-Type** | `multipart/form-data`                                       |
| **Modèles**      | `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`    |

---

## 📥 Paramètres de la Requête

| Paramètre | Type | Requis | Description                 |
|-----------|------|--------|-----------------------------|
| `audio`   | File | ✅ Oui | Fichier audio à transcrire  |

### Formats Audio Supportés

- ✅ **MP3** (.mp3)
- ✅ **WAV** (.wav)
- ✅ **WebM** (.webm)
- ✅ **M4A** (.m4a)
- ✅ **OGG** (.ogg)
- ✅ **FLAC** (.flac)

**⏱️ Durée recommandée:** Jusqu'à 2 minutes (timeout: 120 secondes)

---

## 📤 Réponses de l'API

### ✅ Succès - Audio Darija (HTTP 200)

```json
{
    "transcription": "salam 3likom, kifach nta?",
    "translation": "Hello, how are you?",
    "model": "gemini-2.0-flash"
}
```

### ✅ Succès - Audio Anglais (HTTP 200)

```json
{
    "transcription": "Hello, how are you?",
    "model": "gemini-2.0-flash"
}
```

> **Note:** Le champ `translation` n'apparaît que si l'audio n'est pas en anglais.

### ❌ Erreurs

| Code |                      Message                    |          Description           |
|------|-------------------------------------------------|--------------------------------|
| 400  | `POST required`                                 | Méthode HTTP incorrecte        |
| 400  | `Aucun fichier envoyé`                          | Paramètre `audio` manquant     |
| 500  | `Le traitement du fichier a échoué côté Gemini` | Erreur de traitement Gemini    |
| 504  | `Timeout: le fichier n'a pas pu être traité`    | Délai dépassé (120s)           |

```json
{
    "error": "Message d'erreur détaillé"
}
```

---

## 🔤 Transcription Darija - Alphabet Latin

### Caractères Spéciaux

| Caractère | Son Arabe | Lettre  |        Exemples      |
|-----------|-----------|---------|----------------------|
| **3**     | ع (ayn)   |    ع    | 3afak, 3likom, sa3a  |
| **7**     | ح (ha)    |    ح    | 7a9, 7ta, sba7       |
| **9**     | ق (qaf)   |    ق    | 9ahwa, wa9t, 9alb    |
| **ch**    | ش (shin)  |    ش    | chokran, chnou, mchi |
| **gh**    | غ (ghayn) |    غ    | ghadi, maghrib, ghir |
| **kh**    | خ (kha)   |    خ    | khouh, khdam, khatr  |

### Exemples de Transcription

| Audio Darija (Arabe) | Transcription Latin | Traduction Anglais  |
|----------------------|---------------------|---------------------|
| السلام عليكم         |   salam 3likom      | Peace be upon you   |
| كيفاش نتا؟          |   kifach nta?       | How are you?        |
| لاباس عليك           |   labas 3lik        | Are you okay?       |
| شنو كاين؟           |   chnou kayn?       | What's up?          |
| بغيت قهوة           |   bghit 9ahwa       | I want coffee       |
| شكرا بزاف           |   chokran bzaf      | Thank you very much |
| غادي نمشي           |   ghadi nmchi       | I'm going to leave  |
| واخا                |   wakha             |  Okay                |

---

## 💻 Exemples d'Utilisation

### 1️⃣ cURL (Windows PowerShell)

```powershell
curl -X POST http://localhost:8000/api/speachfrang/default/transcribe/ `
     -F "audio=@C:\chemin\vers\audio.mp3"
```

### 2️⃣ cURL (Linux/Mac)

```bash
curl -X POST http://localhost:8000/api/speachfrang/default/transcribe/ \
     -F "audio=@/chemin/vers/audio.mp3"
```

### 3️⃣ Python (requests)

```python
import requests

url = "http://localhost:8000/api/speachfrang/default/transcribe/"

# Ouvrir le fichier audio
with open('audio.mp3', 'rb') as audio_file:
    files = {'audio': audio_file}
    
    # Envoyer la requête
    response = requests.post(url, files=files)

# Traiter la réponse
if response.status_code == 200:
    result = response.json()
    
    print(f"📝 Transcription: {result['transcription']}")
    print(f"🤖 Modèle: {result['model']}")
    
    # Afficher la traduction si disponible
    if 'translation' in result:
        print(f"🌍 Traduction: {result['translation']}")
else:
    print(f"❌ Erreur: {response.json()['error']}")
```

### 4️⃣ JavaScript (Fetch API)

```javascript
// Depuis un formulaire HTML
const formData = new FormData();
const audioFile = document.getElementById('audioInput').files[0];
formData.append('audio', audioFile);

fetch('http://localhost:8000/api/speachfrang/default/transcribe/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.error) {
        console.error('Erreur:', data.error);
        return;
    }
    
    console.log('Transcription:', data.transcription);
    console.log('Modèle:', data.model);
    
    if (data.translation) {
        console.log('Traduction:', data.translation);
    }
})
.catch(error => console.error('Erreur réseau:', error));
```

### 5️⃣ JavaScript (Axios)

```javascript
import axios from 'axios';

const transcribeAudio = async (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    
    try {
        const response = await axios.post(
            'http://localhost:8000/api/speachfrang/default/transcribe/',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        
        return response.data;
    } catch (error) {
        console.error('Erreur:', error.response?.data?.error || error.message);
        throw error;
    }
};

// Utilisation
const result = await transcribeAudio(myAudioFile);
console.log(result.transcription);
```

### 6️⃣ React (avec hook)

```jsx
import { useState } from 'react';

function DarijaTranscriber() {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('audio', file);

        try {
            const response = await fetch(
                'http://localhost:8000/api/speachfrang/default/transcribe/',
                {
                    method: 'POST',
                    body: formData
                }
            );
            
            const data = await response.json();
            
            if (data.error) {
                setError(data.error);
            } else {
                setResult(data);
            }
        } catch (err) {
            setError('Erreur de connexion');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input type="file" accept="audio/*" onChange={handleFileChange} />
            
            {loading && <p>⏳ Transcription en cours...</p>}
            {error && <p style={{color: 'red'}}>❌ {error}</p>}
            
            {result && (
                <div>
                    <p><strong>📝 Transcription:</strong> {result.transcription}</p>
                    {result.translation && (
                        <p><strong>🌍 Traduction:</strong> {result.translation}</p>
                    )}
                    <p><small>Modèle: {result.model}</small></p>
                </div>
            )}
        </div>
    );
}
```

### 7️⃣ Postman

1. **Méthode:** `POST`
2. **URL:** `http://localhost:8000/api/speachfrang/default/transcribe/`
3. **Body:**
   - Type: `form-data`
   - Key: `audio` (type: **File**)
   - Value: Sélectionner votre fichier audio
4. **Send**

---

## 🔄 Flux de Traitement

```
┌─────────────────┐
│  Fichier Audio  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sauvegarde Temp │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Upload Gemini   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Polling État    │◄──── Attente ACTIVE (max 120s)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transcription   │
│ + Traduction    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Nettoyage       │──── Suppression locale + Gemini
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Réponse JSON    │
└─────────────────┘
```

---

## ⚙️ Configuration

### Démarrage du Serveur

```powershell
# Windows PowerShell
cd c:\cours\Python-Projects\vocale-to-texte

# Activer l'environnement virtuel
.\env\Scripts\Activate

# Lancer le serveur
python manage.py runserver
```

### Dépendances

```powershell
pip install django
pip install djangorestframework
pip install google-genai
```

---

## 🔐 Sécurité en Production

### 1. Variable d'Environnement pour la Clé API

```python
# darija.py - Remplacer la clé hardcodée
import os

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_API_KEY)
```

```powershell
# Windows - Définir la variable
$env:GEMINI_API_KEY = "votre-clé-api"
```

### 2. Limiter la Taille des Fichiers

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25 MB
```

### 3. CORS (si frontend séparé)

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
]
```

---

## 🐛 Résolution de Problèmes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `POST required` | Méthode GET utilisée | Utiliser POST |
| `Aucun fichier envoyé` | Paramètre `audio` manquant | Vérifier le nom du champ |
| `Timeout` | Fichier trop volumineux | Réduire la taille/durée |
| `FAILED_PRECONDITION` | Fichier pas encore ACTIVE | Le polling gère ce cas |
| `403 Forbidden` | CSRF actif | `@csrf_exempt` est appliqué |
| Erreur de connexion | Serveur non lancé | `python manage.py runserver` |

---

## 📊 Comparaison avec les Autres APIs

| Fonctionnalité | `/default/transcribe/` | `/darija/transcribe/` | `/transcribe/` |
|----------------|------------------------|----------------------|----------------|
| **Fichier** | `darija.py` | `darija_api_views.py` | `api_views.py` |
| **Modèle** | Gemini AI | Gemini AI | Whisper |
| **Langues** | Auto-détection | Darija uniquement | FR, EN |
| **Traduction** | ✅ Oui (vers EN) | ❌ Non | ❌ Non |
| **Offline** | ❌ Non | ❌ Non | ✅ Oui |
| **CSRF** | Exempt | Token requis | Token requis |

---

## 📞 Support

Pour toute question :
1. Vérifiez les logs Django
2. Testez avec un fichier court (< 30 secondes)
3. Vérifiez la connexion Internet (API Gemini en ligne)
4. Vérifiez que la clé API Gemini est valide

---

## 🎤 Vocabulaire Darija Utile

| Darija | Arabe | Français | Anglais |
|--------|-------|----------|---------|
| salam 3likom | السلام عليكم | Bonjour | Hello |
| labas | لاباس | Ça va | I'm fine |
| chokran | شكرا | Merci | Thank you |
| bghit | بغيت | Je veux | I want |
| kifach | كيفاش | Comment | How |
| chnou | شنو | Quoi | What |
| fin | فين | Où | Where |
| 3lach | علاش | Pourquoi | Why |
| wakha | واخا | D'accord | Okay |
| bzaf | بزاف | Beaucoup | A lot |
| ghadi | غادي | Je vais | I'm going |
| daba | دابا | Maintenant | Now |
| 9ahwa | قهوة | Café | Coffee |
| khouya | خويا | Mon frère | My brother |
| khti | ختي | Ma sœur | My sister |
