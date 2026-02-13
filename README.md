# 🌍 Fon-Dataset-Generator 🚀

> **"Préserver la langue, cultiver le futur."** — Un outil haute performance pour générer des datasets de traduction Français-Fon de qualité industrielle grâce à l'IA.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](#)
[![Google Sheets](https://img.shields.io/badge/Google_Sheets-Visualiser_le_Dataset-green?style=for-the-badge&logo=googlesheets)](https://docs.google.com/spreadsheets/d/1YGiLHh13jsMZkP04Gi101uc8dgdf-9AOK-u_ymuF8IU/edit?usp=sharing)

---

## 📊 Accès Rapide aux Données

Avant d'explorer le code, vous pouvez consulter le dataset final directement en ligne :
👉 **[Accéder au Google Sheets (Visualisation)](https://docs.google.com/spreadsheets/d/1YGiLHh13jsMZkP04Gi101uc8dgdf-9AOK-u_ymuF8IU/edit?usp=sharing)**

---

## 🌟 Pourquoi ce projet ?

La langue **Fon** (Fongbe) est l'une des langues les plus parlées au Bénin. Pour construire des modèles d'IA (LLM) performants pour notre culture, nous avons besoin de données massives et de qualité.

**Fon-Dataset-Generator** permet de :
- 🧠 **Générer des phrases naturelles** couvrant tous les aspects de la vie quotidienne (santé, commerce, émotions, proverbes).
- 🔄 **Automatiser la traduction** via des APIs modernes.
- 📂 **Exporter en JSONL**, prêt pour le fine-tuning (format OpenAI/DeepSeek).

---

## 🛠️ Deux manières de contribuer

Le projet offre deux approches selon vos besoins :

### 1. Mode Expert (Python Async) ⚡
Idéal pour la génération massive à haute vitesse.
- **Localisation** : `core/generator.py`
- **Avantages** : Asynchrone, multithreadé, gestion des doublons en mémoire.

### 2. Mode Cloud (Google Apps Script) ☁️
Idéal pour ceux qui préfèrent une interface visuelle via Google Sheets.
- **Localisation** : `cloud/GoogleAppsScript.gs`
- **Avantages** : Pas d'installation, sauvegarde directe dans Google Drive, notifications Gmail.
- **Accès direct au Dataset** : [Consulter la version Google Sheets](https://docs.google.com/spreadsheets/d/1YGiLHh13jsMZkP04Gi101uc8dgdf-9AOK-u_ymuF8IU/edit?usp=sharing)

---

## 🚀 Installation & Configuration

### Prérequis (Version Python)
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Bsh54/Fon-Dataset-Generator.git
   cd Fon-Dataset-Generator
   ```
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Configurez vos clés API :
   - Renommez `.env.example` en `.env`.
   - Ajoutez votre `LLM_API_KEY` (OpenAI, DeepSeek ou autre compatible).

### Configuration (Version Google Sheets)
1. Créez un nouveau **Google Sheet**.
2. Allez dans `Extensions > Apps Script`.
3. Copiez le contenu de `cloud/GoogleAppsScript.gs`.
4. Ajoutez vos clés API dans `Paramètres du projet > Propriétés du script`.

---

## 📂 Structure du projet

```text
fon-dataset-generator/
├── core/
│   └── generator.py       # 🧠 Le moteur principal (Python Async)
├── cloud/
│   └── GoogleAppsScript.gs # ☁️ Alternative Cloud pour Google Sheets
├── data/
│   └── dataset_fr_fon.jsonl # 📊 Le dataset généré (Format final)
├── .env.example            # 🔑 Modèle de configuration
├── requirements.txt        # 📦 Dépendances Python
└── README.md               # 📖 Vous êtes ici
```

---

## 📊 Roadmap & Vision 🗺️

- [x] **Architecture modulaire** : Support multi-APIs.
- [x] **Multi-Catégories** : 12 thématiques couvrant 100% des besoins.
- [ ] **Validation par la communauté** : Interface web pour corriger les tons.
- [ ] **Support Audio** : Intégration future pour le Text-to-Speech (TTS).

---

## ❤️ Contribution & Éthique

Ce projet est **Open Source**. La langue est un patrimoine commun.
> "Le code ne doit pas être une barrière, mais un pont entre les cultures."

**Note importante** : Les traductions IA sont une base de travail. Une validation humaine par des locuteurs natifs est toujours recommandée pour garantir l'exactitude des tons.

---
*Généré avec ❤️ pour la culture Béninoise.*
