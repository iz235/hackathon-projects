# 🏥 Hackathon AI Assistant - Projet d'Aidant

Application web **Streamlit** + **OpenAI** pour assistance intelligente d'aidants dans le secteur médical et social.

## 📋 Vue d'ensemble

Prototype développé lors du **Hackathon UPEC** permettant aux aidants professionnels d'obtenir des recommandations intelligentes basées sur **GPT-4** pour mieux assister les patients/résidents.

**Cas d'usage principal:** Assistant d'aidant temps réel pour guidance et support

## 🎯 Fonctionnalités

### Core Features
- 🤖 **Chat IA (OpenAI GPT-4)**
  - Questions/Réponses en temps réel
  - Contexte médical/social
  - Recommandations personnalisées

- 📊 **Analyses Statistiques**
  - Financements disponibles (funding_pie.png)
  - Données démographiques (stats_france.png)
  - Analyse de marché (market_growth.png)
  - Données concurrence (concurrence.png)

- 💾 **Gestion de Données**
  - Base de données JSON (users_db.json)
  - Profils d'utilisateurs
  - Historique d'interactions

- 🤝 **Collaboration**
  - Partage d'informations entre aidants
  - Fiches de suivi

## 📁 Structure du Projet

```
Hackathon_Projet2_Aidant/
├── app.py                       # Application Streamlit
├── app_.py                      # Version alternative
├── requirements.txt             # Dépendances Python
├── test.ipynb                   # Tests & expérimentation
├── index.html                   # Landing page (optionnel)
├── users_db.json                # Base de données locale
├── venv/                        # Environnement virtuel
│
├── Data/
│   ├── cashflow.png             # Graphique flux de trésorerie
│   ├── concurrence.png          # Analyse concurrence
│   ├── finance.png              # Analyses financières
│   ├── funding_pie.png          # Distribution financements
│   ├── market_growth.png        # Croissance marché
│   ├── robot_face.png           # Asset IA
│   └── stats_france.png         # Statistiques France
│
└── .git/                        # Repo Git existant
```

## 🚀 Installation & Setup

### Prérequis

- **Python 3.8+**
- **pip** ou **conda**
- **Clé API OpenAI** (gratuit ou payant)
- **Git**

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/iz235/hackathon-projects.git
cd Hackathon_Projet2_Aidant

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux/Mac
# ou
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
# Créer un fichier .env
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "DATABASE_PATH=./users_db.json" >> .env

# 5. Lancer l'app
streamlit run app.py

# Ouvre automatiquement: http://localhost:8501
```

## 💻 Dépendances

```
streamlit           # Framework web
openai              # Client OpenAI API
python-dotenv       # Gestion variables d'env
langchain           # LLM orchestration
langchain-openai    # OpenAI integration
```

## 🤖 Utilisation

### Interface Utilisateur

**Page d'Accueil:**
```
┌─────────────────────────────────────────┐
│      🏥 Assistant Aidant Intelligente   │
├─────────────────────────────────────────┤
│ Bienvenue! Je suis votre assistant IA  │
│ Poser vos questions d'aide...          │
├─────────────────────────────────────────┤
│ [Chat Box]                              │
│ Tapez votre question...                │
│ [Envoyer]                              │
└─────────────────────────────────────────┘
```

### Exemples d'Utilisation

```
Utilisateur:
"Comment puis-je aider un patient atteint d'Alzheimer?"

IA:
"Voici quelques recommandations:
1. Créer une routine structurée
2. Utiliser des aides visuelles
3. Parler lentement et clairement
4. Être patient et empathique
5. Contacter des ressources spécialisées"
```

### Cas d'Usage

| Cas | Exemple |
|-----|---------|
| Conseil médical | "Quels sont les symptômes de..."  |
| Aide psycho-sociale | "Comment gérer le stress du patient?" |
| Procédures administratives | "Aides financières disponibles?" |
| Support émotionnel | "Je suis fatigué, comment tenir?" |

## 📊 Tableau de Bord

L'app inclut des visualisations:

```
📈 Graphiques:
├── Funding Distribution (Pie Chart)
├── Market Growth (Line Chart)
├── France Statistics (Bar Chart)
├── Competitor Analysis (Comparison)
└── Cash Flow (Flow Diagram)
```

## 🗄️ Gestion de Données

### Structure users_db.json

```json
{
  "users": [
    {
      "id": "user001",
      "name": "Jean Dupont",
      "role": "Aidant",
      "experience": 5,
      "patients": ["P001", "P002"],
      "created_at": "2026-01-15",
      "last_interaction": "2026-05-06"
    }
  ],
  "patients": [
    {
      "id": "P001",
      "name": "Marie Martin",
      "age": 78,
      "conditions": ["Alzheimer", "Hypertension"],
      "care_level": "High"
    }
  ]
}
```

### Opérations Clés

```python
import json

# Charger
with open('users_db.json') as f:
    data = json.load(f)

# Sauvegarder
with open('users_db.json', 'w') as f:
    json.dump(data, f, indent=2)

# Ajouter utilisateur
data['users'].append({
    "id": "new_id",
    "name": "Nouveau Aidant"
})
```

## 🔐 Configuration API OpenAI

### Obtenir une Clé API

1. Visiter: https://platform.openai.com/api-keys
2. Créer une nouvelle clé (ou utiliser existante)
3. Copier dans `.env`

```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

### Modèles Disponibles

| Modèle | Vitesse | Coût | Usage |
|--------|---------|------|-------|
| gpt-4o | Lent | Cher | Réponses complexes |
| gpt-4-turbo | Moyen | Moyen | Équilibre |
| gpt-3.5-turbo | Rapide | Pas cher | Prototypage |

### Configuration du Modèle

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.7,  # Créativité (0-1)
    max_tokens=2000   # Limite de réponse
)

response = llm.invoke("Votre question")
```

## 📱 Interface Streamlit

### Composants Utilisés

```python
import streamlit as st

# Titre
st.title("🏥 Assistant Aidant")

# Chat
message = st.chat_input("Votre question...")

# Afficher messages
st.chat_message("user")
st.write("Question de l'utilisateur")

st.chat_message("assistant")
st.write("Réponse de l'IA")

# Sidebar
with st.sidebar:
    st.subheader("Options")
    model = st.selectbox("Modèle", ["gpt-4o", "gpt-4-turbo"])
    temp = st.slider("Température", 0.0, 1.0, 0.7)

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Utilisateurs", 245)
with col2:
    st.metric("Interactions", 1234)
with col3:
    st.metric("Satisfaction", "92%")
```

## 🧪 Tests

```bash
# Lancer les tests
pytest test.ipynb

# Avec couverture
coverage run -m pytest
coverage report
```

## 🔮 Roadmap

- [x] Chat IA de base
- [x] Gestion utilisateurs
- [x] Visualisations statiques
- [ ] Base de données PostgreSQL
- [ ] Authentification utilisateur
- [ ] Multi-langue (EN/FR)
- [ ] Export de rapports
- [ ] API REST (FastAPI)
- [ ] Application mobile
- [ ] Intégration SMS/WhatsApp

## 📚 Ressources

- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [LangChain Documentation](https://python.langchain.com/)
- [Python-dotenv](https://python-dotenv.readthedocs.io/)

## ⚠️ Considérations Éthiques

- 🔒 **Confidentialité:** Données patient protégées
- 🚫 **Limites:** L'IA ne remplace pas un professionnel
- 📋 **Responsabilité:** Vérifier les recommandations
- 🎯 **Consentement:** Accord patient requis
- 📊 **Traçabilité:** Toutes les interactions loggées

## 🐛 Troubleshooting

### Erreur: "Invalid API Key"
```bash
# Vérifier le .env
cat .env

# Créer nouveau .env
echo "OPENAI_API_KEY=sk-xxx" > .env
```

### App Streamlit ne lance pas
```bash
streamlit run app.py --logger.level=debug
```

### Problème de connexion OpenAI
- Vérifier internet
- Vérifier la clé API
- Vérifier les quotas OpenAI

## 👤 Auteur
**Izadine** - AI Developer & Healthcare Tech  
Email: massarizzadinealkhali@gmail.com  
GitHub: [@iz235](https://github.com/iz235)

## 📄 Licence
MIT License

---
**État:** 🟢 Fonctionnel  
**Dernière Mise à Jour:** Mai 2026  
**Contexte:** Hackathon UPEC 2026
