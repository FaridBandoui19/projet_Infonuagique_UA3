🤖 Landon Hotel Chatbot — Projet UA3
Chatbot documentaire qui répond strictement sur le contenu du PDF Landon-Hotel Brand Guidelines.
Il utilise OpenAI (modèle gpt-4o-mini), LangChain pour le prompt + sélection de contexte, et Flask pour l’API + une petite UI web.

🎯 Objectif pédagogique : extraire un PDF, bâtir un prompt “persona”, injecter le contexte, exposer une API et une interface simple — puis présenter/démontrer le tout.

🖼️ Aperçu

Zone de chat minimale (HTML/JS)

API Flask (/chatbot) qui appelle le LLM avec un contexte extrait du PDF

Persona : “Mr. Landon”, ne parle que de Landon Hotel (brand, logo, couleurs, services, typo, etc.)

✨ Fonctionnalités
Extraction PDF → texte (pré-traitement)

Sélection intelligente de contexte (ancrages par section : “OUR COLORS”, “LOGO SYSTEM”, “TYPOGRAPHY SYSTEM”…)

Persona contrôlée (salut/merci → réponse chaleureuse + suggestions)

Détection de langue (FR par défaut)

API REST ( /health, /chatbot)

UI web simple (HTML + fetch)

Gestion d’erreurs basiques (entrées vides, erreurs serveur)

🧭 Sommaire
Architecture & Arborescence

Prérequis

Installation

Configuration (.env)

Lancement pas à pas

API

Frontend (UI)

Dépannage

Améliorations futures

Crédits & Licence

🏗️ Architecture & Arborescence
bash
Copier
Modifier
Projet AI chatbot/
├─ 01 Collecte et préparation des données PDF/
│  ├─ Landon-Hotel.pdf
│  └─ Collecte et préparation des données PDF.py   # extrait → pdf_text.txt
│     └─ pdf_text.txt                              # ⚠️ ICI (généré)
├─ 02 Utiliser API OpenAI/
│  └─ 02_test_llm_sur_pdf.py                       # test simple sans LangChain
├─ 03 Intégrer LangChain/
│  └─ Intégrer LangChain.py                        # prompt + contexte + demo CLI
├─ 04 Flask/
│  ├─ app.py                                       # API + serveur Flask
│  └─ templates/
│     └─ index.html                                # UI du chatbot
├─ 05 HTMLCSS/                                     # (assets si besoin)
├─ .env                                            # ***non commité*** (OPENAI_API_KEY)
├─ requirements.txt
└─ docs/
   └─ screenshot.png
✅ Important : pdf_text.txt est dans 01 Collecte et préparation des données PDF/.
Pas besoin de le dupliquer à la racine. Le code sait le retrouver automatiquement.

✅ Prérequis
Python 3.10+ (idéal 3.11/3.12)

Un compte OpenAI avec crédits (sinon insufficient_quota / 429)

Accès Internet

Windows/macOS/Linux (exemples ci-dessous Windows + Git Bash/PowerShell)

📦 Installation
Cloner/ouvrir le projet dans VS Code.

Créer un virtualenv & activer :

PowerShell

powershell
Copier
Modifier
python -m venv .venv
.venv\Scripts\Activate.ps1
Git Bash

bash
Copier
Modifier
python -m venv .venv
source .venv/Scripts/activate
Installer les dépendances :

bash
Copier
Modifier
pip install -r requirements.txt
🔐 Configuration (.env)
Crée un fichier .env à la racine :

ini
Copier
Modifier
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
# (Optionnel) Forcer un chemin si besoin :
# PDF_TEXT_PATH=01 Collecte et préparation des données PDF/pdf_text.txt
.env ne doit jamais être commité (vérifie .gitignore).

▶️ Lancement pas à pas
Étape 1 — Extraire le PDF → pdf_text.txt
Depuis le dossier racine :

bash
Copier
Modifier
python "01 Collecte et préparation des données PDF/Collecte et préparation des données PDF.py"
Tu dois voir un message du style :

bash
Copier
Modifier
✅ Extraction OK → .../01 Collecte et préparation des données PDF/pdf_text.txt
Étape 2 — Test rapide OpenAI (sans LangChain)
bash
Copier
Modifier
python "02 Utiliser API OpenAI/02_test_llm_sur_pdf.py"
Vérifie que :

la clé OpenAI est OK,

le fichier pdf_text.txt est bien lu,

la réponse revient.

Étape 3 — Intégration LangChain (CLI)
bash
Copier
Modifier
python "03 Intégrer LangChain/Intégrer LangChain.py"
Exécute 2–3 questions : “Bonjour”, “Quels sont vos services ?”, “Parle-moi de la typographie”, etc.

Étape 4 — API + UI Flask
bash
Copier
Modifier
python "04 Flask/app.py"
Ouvre le navigateur sur http://127.0.0.1:5000 et discute avec “Mr. Landon”.

🔌 API
GET /health
Réponse :

json
Copier
Modifier
{ "status": "ok" }
POST /chatbot
Requête

json
Copier
Modifier
{ "question": "Parle-moi des couleurs de la marque" }
Réponse — succès

json
Copier
Modifier
{ "ok": true, "response": "…réponse formatée…" }
Réponse — erreur

json
Copier
Modifier
{ "ok": false, "error": "Message d’erreur lisible" }
🖥️ Frontend (UI)
04 Flask/templates/index.html :
Interface minimaliste (input + bouton) qui appelle POST /chatbot via fetch.

Améliorable avec :

indicateur “en train d’écrire…”

gestion 429 (afficher “beaucoup de demandes, réessayez”)

joli scroll & bulles chat

La logique côté serveur est stateless : aucune session stockée.

🧯 Dépannage
FileNotFoundError: pdf_text.txt

Lance d’abord l’étape 1 (extraction).

Vérifie l’emplacement : 01 Collecte et préparation des données PDF/pdf_text.txt.

En dernier recours, fixe PDF_TEXT_PATH dans .env.

openai.RateLimitError (429) / insufficient_quota

Attends 5–15 sec et réessaye (429).

Vérifie l’onglet Billing de OpenAI (crédits actifs).

Évite d’envoyer des messages très longs.

Mauvaise clé (401)

Assure-toi que .env contient OPENAI_API_KEY correct, et que le venv est activé.

Unicode/accents

Toutes les lectures/écritures fichiers sont en utf-8.

Si tu obtiens des ‘�’, assure-toi que le PDF s’extrait proprement (ou change de lib d’extraction).

🚀 Améliorations futures
RAG plus costaud (FAISS/Chroma + embeddings) au lieu de simple slicing

Streaming des tokens pour une UX fluide

Moderation & filtres de sûreté

Mémoire courte (résumer les tours précédents)

CI/CD (GitHub Actions) + déploiement (Render/Fly.io/Cloud Run)

Tests unitaires (sélecteur de contexte, routes Flask)

🙌 Crédits & Licence
Contenu PDF : Landon Hotel — Brand Guidelines (document fourni dans le cadre du cours).

Libs : OpenAI, LangChain, Flask, python-dotenv.

Licence : MIT (adapter si vos contraintes de cours l’exigent).

📝 Notes d’implémentation
Le serveur cherche automatiquement pdf_text.txt dans :

01 Collecte et préparation des données PDF/pdf_text.txt ✅ (ton cas)

PDF_TEXT_PATH (si défini dans .env)

./pdf_text.txt (fallback)

La sélection de contexte utilise des ancres robustes (ex. “OUR COLORS”, “LOGO SYSTEM”, “TYPOGRAPHY SYSTEM”, etc.) pour s’adapter au texte extrait, même si l’espacement/accents diffèrent.