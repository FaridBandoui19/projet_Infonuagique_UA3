# Version 07
from dotenv import load_dotenv
import os
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import traceback

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY manquante dans .env")

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / "01 Collecte et préparation des données PDF" / "pdf_text.txt",
    ROOT / "pdf_text.txt",
    Path.cwd() / "pdf_text.txt",
]
TXT_PATH = next((p for p in CANDIDATES if p.exists()), None)
if not TXT_PATH:
    tried = "\n- ".join(str(p) for p in CANDIDATES)
    raise FileNotFoundError("Impossible de trouver pdf_text.txt. Emplacements testés:\n- " + tried)

FULL_DOC = TXT_PATH.read_text(encoding="utf-8")
UPPER = FULL_DOC.upper()

def select_context(question: str, doc: str, max_chars: int = 15000) -> str:
    q = (question or "").lower()
    UP = doc.upper()

    def find_idx(anchor: str) -> int:
        return UP.find(anchor.upper())

    def slice_around(idx: int, before: int = 1500, after: int = 4500) -> str:
        if idx < 0:
            return ""
        start = max(0, idx - before)
        end = min(len(doc), idx + after)
        return doc[start:end]

    if any(k in q for k in ["typograph", "police", "font", "typo"]):
        anchors = [
            "TYPOGRAPHY SYSTEM","OUR PRIMARY TYPEFACE","BRANDON GROTESQUE",
            "OUR ACCENT TYPEFACE","ESSONNES","TYPOGRAPHY USAGE",
        ]
        parts = []
        for a in anchors:
            chunk = slice_around(find_idx(a))
            if chunk:
                parts.append(chunk)
        if parts:
            return ("\n\n---\n\n".join(parts))[:max_chars]

    themes = [
        (["service","commodit","amenit","équipement"],
         ["OUR SERVICES & AMENITIES","OUR SERVICES","AMENITIES"]),
        (["logo","logotype","logomark","marque"],
         ["LOGO SYSTEM","OUR LOGO","LOGOTYPE","OUR LOGOTYPE",
          "LOGOMARK","OUR LOGOMARK","LOGO LOCK-UP","LOGO USAGE",
          "SECONDARY SUBMARKS","LOGO COMPONENTS & CONSTRUCTION"]),
        (["couleur","color"],
         ["COLOR SYSTEM","OUR COLORS","COLOR CODES","BACKGROUND COLORS",
          "WEB ACCESSIBLE COLORS","COLOR USAGE"]),
        (["graphique","icône","icone","pattern","motif","bannière","banniere"],
         ["SUPPORTING GRAPHICS","OUR ICONS","OUR PATTERNS","BANNER GRAPHIC"]),
        (["photo","photograph"],["PHOTOGRAPHY","STYLE","COMPOSITION","LIGHTING","COLOR"]),
        (["valeur","mission","vision","slogan","purpose"],
         ["OUR VALUES","MISSION STATEMENT","VISION STATEMENT","OUR SLOGAN","BRAND FOUNDATION"]),
        (["papier","facture","newsletter","sales sheet","stationery","devis","invoice"],
         ["BRANDED MATERIALS","STATIONERY","NEWSLETTER","INVOICE","SALES SHEET"]),
    ]

    for keys, anchors in themes:
        if any(k in q for k in keys):
            for a in anchors:
                i = UPPER.find(a.upper())
                if i != -1:
                    return slice_around(i, before=max_chars//4, after=max_chars//2)

    for fb in ["BRANDON GROTESQUE","OUR COLORS","OUR SERVICES","PHOTOGRAPHY"]:
        i = UPPER.find(fb.upper())
        if i != -1:
            return slice_around(i, before=max_chars//4, after=max_chars//2)

    return doc[:max_chars]

system_rules = """You are "Mr. Landon", the hotel manager persona for Landon Hotel.
You ONLY discuss Landon Hotel topics (brand, services, amenities, visual identity, etc.), grounded in the provided document.
Do NOT refuse greetings/pleasantries—reply warmly, then invite a Landon-related question.
Rules:
- Detect the user's language (default to French for this user); reply in the user's language.
- For greetings/thanks/small talk ("bonjour", "hello", "salut", "merci", etc.):
  • Respond briefly and warmly as Mr. Landon.
  • Then offer 3 quick example topics about Landon Hotel.
- If the question is ambiguous or likely out-of-scope:
  • Ask one short clarifying question and propose 2–3 Landon-related directions.
- If it's clearly unrelated AFTER a clarification, say: "I can't assist you with that, sorry!" and immediately propose relevant Landon topics.
- When info is not in the document, say what you DO know (from the doc) and suggest who/where to ask for the rest (concierge, website).
- Keep answers concise, structured, and friendly.
- Base every factual detail strictly on CONTEXTE.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_rules),
    ("user", "CONTEXTE:\n{context}\n\nQUESTION:\n{question}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm

def answer_question(question: str) -> str:
    ctx = select_context(question, FULL_DOC)
    resp = chain.invoke({"context": ctx, "question": question})
    return getattr(resp, "content", str(resp))

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/chatbot")
def chatbot():
    try:
        data = request.get_json(force=True, silent=True) or {}
        question = (data.get("question") or "").strip()
        if not question:
            return jsonify({"ok": False, "error": "Question vide."}), 400
        ans = answer_question(question)
        return jsonify({"ok": True, "response": ans})
    except Exception:
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Erreur interne."}), 500

if __name__ == "__main__":
    app.run(debug=True)












# # Version 06
# # 04 Flask/app.py

# from dotenv import load_dotenv
# import os
# from pathlib import Path
# from flask import Flask, request, jsonify
# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# import traceback

# # --- .env ---
# load_dotenv()
# if not os.getenv("OPENAI_API_KEY"):
#     raise RuntimeError("OPENAI_API_KEY manquante dans .env")

# # --- Localiser pdf_text.txt (mêmes règles que précédemment) ---
# ROOT = Path(__file__).resolve().parents[1]  # racine du projet
# CANDIDATES = [
#     ROOT / "01 Collecte et préparation des données PDF" / "pdf_text.txt",
#     ROOT / "pdf_text.txt",
#     Path.cwd() / "pdf_text.txt",
# ]
# TXT_PATH = next((p for p in CANDIDATES if p.exists()), None)
# if not TXT_PATH:
#     tried = "\n- ".join(str(p) for p in CANDIDATES)
#     raise FileNotFoundError("Impossible de trouver pdf_text.txt. Emplacements testés:\n- " + tried)

# FULL_DOC = TXT_PATH.read_text(encoding="utf-8")
# UPPER = FULL_DOC.upper()

# # --- Sélecteur de contexte (version patch typographie) ---
# def select_context(question: str, doc: str, max_chars: int = 15000) -> str:
#     q = (question or "").lower()
#     UP = doc.upper()

#     def find_idx(anchor: str) -> int:
#         return UP.find(anchor.upper())

#     def slice_around(idx: int, before: int = 1500, after: int = 4500) -> str:
#         if idx < 0:
#             return ""
#         start = max(0, idx - before)
#         end = min(len(doc), idx + after)
#         return doc[start:end]

#     # Typographie: assembler plusieurs sections
#     if any(k in q for k in ["typograph", "police", "font", "typo"]):
#         anchors = [
#             "TYPOGRAPHY SYSTEM",
#             "OUR PRIMARY TYPEFACE",
#             "BRANDON GROTESQUE",
#             "OUR ACCENT TYPEFACE",
#             "ESSONNES",
#             "TYPOGRAPHY USAGE",
#         ]
#         parts = []
#         for a in anchors:
#             idx = find_idx(a)
#             chunk = slice_around(idx)
#             if chunk:
#                 parts.append(chunk)
#         if parts:
#             return ("\n\n---\n\n".join(parts))[:max_chars]

#     themes = [
#         (["service", "commodit", "amenit", "équipement"], [
#             "OUR SERVICES & AMENITIES", "OUR SERVICES", "AMENITIES"
#         ]),
#         (["logo", "logotype", "logomark", "marque"], [
#             "LOGO SYSTEM", "OUR LOGO", "LOGOTYPE", "OUR LOGOTYPE",
#             "LOGOMARK", "OUR LOGOMARK", "LOGO LOCK-UP", "LOGO USAGE",
#             "SECONDARY SUBMARKS", "LOGO COMPONENTS & CONSTRUCTION"
#         ]),
#         (["couleur", "color"], [
#             "COLOR SYSTEM", "OUR COLORS", "COLOR CODES", "BACKGROUND COLORS",
#             "WEB ACCESSIBLE COLORS", "COLOR USAGE"
#         ]),
#         (["graphique", "icône", "icone", "pattern", "motif", "bannière", "banniere"], [
#             "SUPPORTING GRAPHICS", "OUR ICONS", "OUR PATTERNS", "BANNER GRAPHIC"
#         ]),
#         (["photo", "photograph"], [
#             "PHOTOGRAPHY", "STYLE", "COMPOSITION", "LIGHTING", "COLOR"
#         ]),
#         (["valeur", "mission", "vision", "slogan", "purpose"], [
#             "OUR VALUES", "MISSION STATEMENT", "VISION STATEMENT",
#             "OUR SLOGAN", "BRAND FOUNDATION"
#         ]),
#         (["papier", "facture", "newsletter", "sales sheet", "stationery", "devis", "invoice"], [
#             "BRANDED MATERIALS", "STATIONERY", "NEWSLETTER", "INVOICE", "SALES SHEET"
#         ]),
#     ]

#     def first_anchor_idx(anchors):
#         for a in anchors:
#             i = UPPER.find(a.upper())
#             if i != -1:
#                 return i
#         return -1

#     for keys, anchors in themes:
#         if any(k in q for k in keys):
#             i = first_anchor_idx(anchors)
#             if i != -1:
#                 return slice_around(i, before=max_chars // 4, after=max_chars // 2)

#     for fb in ["BRANDON GROTESQUE", "OUR COLORS", "OUR SERVICES", "PHOTOGRAPHY"]:
#         i = UPPER.find(fb.upper())
#         if i != -1:
#             return slice_around(i, before=max_chars // 4, after=max_chars // 2)

#     return doc[:max_chars]

# # --- Règles système (persona) ---
# system_rules = """You are "Mr. Landon", the hotel manager persona for Landon Hotel.
# You ONLY discuss Landon Hotel topics (brand, services, amenities, visual identity, etc.), grounded in the provided document.
# Do NOT refuse greetings/pleasantries—reply warmly, then invite a Landon-related question.

# Rules:
# - Detect the user's language (default to French for this user); reply in the user's language.
# - For greetings/thanks/small talk ("bonjour", "hello", "salut", "merci", etc.):
#   • Respond briefly and warmly as Mr. Landon.
#   • Then offer 3 quick example topics about Landon Hotel.
# - If the question is ambiguous or likely out-of-scope:
#   • Ask one short clarifying question and propose 2–3 Landon-related directions.
# - If it's clearly unrelated AFTER a clarification, say: "I can't assist you with that, sorry!" and immediately propose relevant Landon topics.
# - When info is not in the document, say what you DO know (from the doc) and suggest who/where to ask for the rest (concierge, website).
# - Keep answers concise, structured, and friendly.
# - Base every factual detail strictly on CONTEXTE.
# """

# prompt = ChatPromptTemplate.from_messages([
#     ("system", system_rules),
#     ("user", "CONTEXTE:\n{context}\n\nQUESTION:\n{question}")
# ])

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# chain = prompt | llm

# def answer_question(question: str) -> str:
#     ctx = select_context(question, FULL_DOC)
#     resp = chain.invoke({"context": ctx, "question": question})
#     return getattr(resp, "content", str(resp))

# # --- Flask ---
# app = Flask(__name__)

# @app.get("/health")
# def health():
#     return jsonify({"status": "ok"})

# @app.post("/chatbot")
# def chatbot():
#     try:
#         data = request.get_json(force=True, silent=True) or {}
#         question = (data.get("question") or "").strip()
#         if not question:
#             return jsonify({"ok": False, "error": "Question vide."}), 400
#         ans = answer_question(question)
#         return jsonify({"ok": True, "response": ans})
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({"ok": False, "error": "Erreur interne."}), 500

# if __name__ == "__main__":
#     app.run(debug=True)


















# # Version 05

# from flask import Flask, render_template, request, jsonify
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# import os, re, traceback

# load_dotenv()
# if not os.getenv("OPENAI_API_KEY"):
#     print("⚠️  OPENAI_API_KEY manquante dans .env")

# # Contexte
# with open("pdf_text.txt", "r", encoding="utf-8") as f:
#     context = f.read()
# context = context[:4000]  # sécurité simple

# template = context + """
# You are "Mr. Landon", the hotel manager persona for Landon Hotel. 
# You ONLY discuss Landon Hotel topics (brand, services, amenities, visual identity, etc.), ideally grounded in the provided document.
# However, DO NOT refuse for greetings or pleasantries—reply warmly, then invite a Landon-related question.

# Rules:
# - Detect the user's language (French by default for this user; reply in the user's language).
# - For greetings/thanks/small talk: respond warmly + offer 3 Landon topics.
# - If ambiguous: ask a short clarifying question + propose 2–3 Landon directions.
# - If clearly unrelated AFTER clarification: say "I can't assist you with that, sorry!" + propose relevant Landon topics.
# - Keep answers concise, structured, and friendly.

# Question: {question}
# Answer:
# """

# tmpl = PromptTemplate(input_variables=["question"], template=template)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# chain = tmpl | llm

# GREETINGS = re.compile(r"^\s*(salut|bonjour|bonsoir|hello|hi|hey|salam|marhaba)\b", re.I)
# THANKS = re.compile(r"\b(merci|thanks|thank you|choukran)\b", re.I)
# FASTLANE = ("Bonjour 👋 Je suis Mr. Landon. "
#             "Souhaitez-vous : 1) services & équipements, 2) identité visuelle (logo/couleurs/typo), "
#             "ou 3) valeurs & slogan ?")

# def smalltalk(q: str):
#     if not q: return None
#     if GREETINGS.search(q) or THANKS.search(q):
#         return FASTLANE
#     return None

# def reply(q: str) -> str:
#     quick = smalltalk(q)
#     if quick: return quick
#     resp = chain.invoke({"question": q})
#     return resp.content if hasattr(resp, "content") else str(resp)

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chatbot", methods=["POST"])
# def chatbot():
#     try:
#         data = request.get_json(force=True, silent=True) or {}
#         question = (data.get("question") or "").strip()
#         if not question:
#             return jsonify({"ok": False, "error": "Question vide."}), 400
#         answer = reply(question)
#         return jsonify({"ok": True, "response": answer})
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"ok": False, "error": "Erreur interne."}), 500

# if __name__ == "__main__":
#     app.run(debug=True)







# # version 4

# from flask import Flask, render_template, request, jsonify
# from langchain_openai import ChatOpenAI  # ✅ Chat model
# from langchain.prompts import PromptTemplate
# from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
# import re, traceback, os

# # -------- Chargement & troncature du contexte (provisoire) --------
# with open('pdf_text.txt', 'r', encoding='utf-8') as f:
#     _raw = f.read()

# # ⚠️ Simple troncature pour limiter les tokens (à remplacer plus tard par une vraie RAG)
# MAX_CTX_CHARS = 4000
# context = _raw[:MAX_CTX_CHARS]

# hotel_assistant_template = context + """
# You are "Mr. Landon", the hotel manager persona for Landon Hotel. 
# You ONLY discuss Landon Hotel topics (brand, services, amenities, visual identity, etc.), ideally grounded in the provided document.
# However, DO NOT refuse for greetings or pleasantries—reply warmly, then invite a Landon-related question.

# Rules:
# - Detect the user's language (French by default for this user; reply in the user's language).
# - For greetings/thanks/small talk ("bonjour", "hello", "salut", "merci", etc.):
#   • Respond briefly and warmly as Mr. Landon.
#   • Then guide the user: offer 3 quick example topics about Landon Hotel.
# - If the question is ambiguous or likely out-of-scope:
#   • Ask a short clarifying question and suggest 2-3 Landon-related directions.
# - If it's clearly unrelated AFTER a clarification, then say: "I can't assist you with that, sorry!" and immediately propose relevant Landon topics.
# - When info is not in the document, say what you DO know (from the doc), and suggest who/where to ask for the rest (concierge, website, etc.).
# - Keep answers concise, structured, and friendly.

# Question: {question}
# Answer:
# """

# hotel_assistant_prompt_template = PromptTemplate(
#     input_variables=["question"],
#     template=hotel_assistant_template
# )

# # ✅ ChatOpenAI + paramètres sobres
# llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
# llm_chain = hotel_assistant_prompt_template | llm

# # -------- Fastlane: éviter l'API pour small talk --------
# GREETINGS = re.compile(r"^\s*(salut|bonjour|bonsoir|hello|hi|hey|salam|marhaba)\b", re.I)
# THANKS = re.compile(r"\b(merci|thanks|thank you|choukran)\b", re.I)

# FASTLANE_REPLY = ("Bonjour 👋 Je suis Mr. Landon. "
#                   "Je peux répondre à vos questions sur Landon Hotel. "
#                   "Préférez-vous : 1) services & équipements, 2) identité visuelle (logo/couleurs/typo), "
#                   "ou 3) valeurs & slogan ?")

# def fastlane_smalltalk(text: str):
#     if not text:
#         return None
#     if GREETINGS.search(text) or THANKS.search(text):
#         return FASTLANE_REPLY
#     return None

# # -------- Retry sur 429 --------
# from openai import RateLimitError

# @retry(
#     reraise=True,
#     stop=stop_after_attempt(4),  # 4 tentatives max
#     wait=wait_random_exponential(multiplier=1, max=8),  # backoff avec jitter
#     retry=retry_if_exception_type(RateLimitError)
# )
# def _invoke_llm(payload: dict):
#     return llm_chain.invoke(payload)

# def query_llm(question: str) -> str:
#     # Fastlane
#     quick = fastlane_smalltalk(question)
#     if quick:
#         return quick

#     # Appel LLM avec retry
#     resp = _invoke_llm({'question': question})
#     try:
#         return resp.content if hasattr(resp, "content") else str(resp)
#     except Exception:
#         return str(resp)

# # -------- Flask --------
# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chatbot", methods=["POST"])
# def chatbot():
#     try:
#         data = request.get_json(force=True, silent=True) or {}
#         question = (data.get("question") or "").strip()
#         if not question:
#             return jsonify({"ok": False, "error": "Question vide."}), 400

#         answer = query_llm(question)
#         return jsonify({"ok": True, "response": answer})

#     except RateLimitError:
#         # On renvoie 429 pour permettre au front d'afficher un message adapté
#         return jsonify({"ok": False, "error": "Le service est momentanément saturé. Réessayez dans quelques secondes."}), 429
#     except Exception:
#         traceback.print_exc()
#         return jsonify({"ok": False, "error": "Une erreur interne est survenue."}), 500

# @app.route("/health")
# def health():
#     return jsonify({"status": "ok"})

# if __name__ == "__main__":
#     # Assure-toi que OPENAI_API_KEY est bien défini dans ton environnement
#     if not os.getenv("OPENAI_API_KEY"):
#         print("⚠️  OPENAI_API_KEY n'est pas défini dans l'environnement.")
#     app.run(debug=True)




# # version 3
# from flask import Flask, render_template, request, jsonify
# from langchain_openai import OpenAI
# from langchain.prompts import PromptTemplate
# import traceback

# # Charger le texte du PDF
# with open('pdf_text.txt', 'r', encoding='utf-8') as f:
#     prompt = f.read()

# hotel_assistant_template = prompt + """
# You are "Mr. Landon", the hotel manager persona for Landon Hotel. 
# You ONLY discuss Landon Hotel topics (brand, services, amenities, visual identity, etc.), ideally grounded in the provided document.
# However, DO NOT refuse for greetings or pleasantries—reply warmly, then invite a Landon-related question.

# Rules:
# - Detect the user's language (French by default for this user; reply in the user's language).
# - For greetings/thanks/small talk ("bonjour", "hello", "salut", "merci", etc.):
#   • Respond briefly and warmly as Mr. Landon.
#   • Then guide the user: offer 3 quick example topics about Landon Hotel.
# - If the question is ambiguous or likely out-of-scope:
#   • Ask a short clarifying question and suggest 2-3 Landon-related directions.
# - If it's clearly unrelated AFTER a clarification, then say: "I can't assist you with that, sorry!" and immediately propose relevant Landon topics.
# - When info is not in the document, say what you DO know (from the doc), and suggest who/where to ask for the rest (concierge, website, etc.).
# - Keep answers concise, structured, and friendly.

# Question: {question}
# Answer:
# """

# hotel_assistant_prompt_template = PromptTemplate(
#     input_variables=["question"],
#     template=hotel_assistant_template
# )

# llm = OpenAI(model='gpt-4o-mini', temperature=0)
# llm_chain = hotel_assistant_prompt_template | llm

# def query_llm(question: str) -> str:
#     resp = llm_chain.invoke({'question': question})
#     # LangChain peut renvoyer soit une string soit un Message ; on normalise
#     try:
#         return resp.content if hasattr(resp, "content") else str(resp)
#     except Exception:
#         return str(resp)

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chatbot", methods=["POST"])
# def chatbot():
#     try:
#         data = request.get_json(force=True, silent=True) or {}
#         question = (data.get("question") or "").strip()
#         if not question:
#             return jsonify({"ok": False, "error": "Question vide."}), 400

#         answer = query_llm(question)
#         return jsonify({"ok": True, "response": answer})
#     except Exception as e:
#         # Log serveur + message client propre
#         traceback.print_exc()
#         return jsonify({"ok": False, "error": "Une erreur interne est survenue."}), 500

# @app.route("/health")
# def health():
#     return jsonify({"status": "ok"})
    
# if __name__ == "__main__":
#     app.run(debug=True)




# # Verson 2

# from flask import Flask, render_template, request, jsonify
# from langchain_openai import OpenAI
# from langchain.prompts import PromptTemplate

# # 🎯 Étape cruciale : Assurez-vous que 'pdf_text.txt' est le fichier que vous lisez.
# # Ce fichier contient tout le contenu de votre Landon-Hotel.pdf.
# prompt = open('pdf_text.txt', 'r', encoding='utf-8').read() 

# # Définition du template pour le prompt. C'est ici que la "personnalité" du chatbot est définie
# # et que le contenu de votre PDF est injecté comme base de connaissances.
# hotel_assistant_template = prompt + """
# You are the hotel manager of Landon Hotel, named "Mr. Landon". 
# Your expertise is exclusively in providing information and advice about anything related to Landon Hotel. 
# This includes any general Landon Hotel related queries. 
# You do not provide information outside of this scope. 
# If a question is not about Landon Hotel, respond with, "I can't assist you with that, sorry!" 
# Question: {question} 
# Answer: 
# """

# # Création de l'objet PromptTemplate de LangChain.
# # Il indique que 'question' est la seule variable d'entrée que le template attend.
# hotel_assistant_prompt_template = PromptTemplate( 
#     input_variables=["question"], 
#     template=hotel_assistant_template 
# ) 

# # Initialisation du modèle OpenAI.
# # 🚀 Changement du modèle vers 'gpt-4o-mini' comme convenu.
# # temperature=0 est maintenue pour des réponses précises et factuelles, non créatives.
# llm = OpenAI(model='gpt-4o-mini', temperature=0) 

# # Création de la chaîne LangChain (LLMChain).
# # Le pipe '|' envoie la sortie du prompt formaté directement au modèle de langage.
# llm_chain = hotel_assistant_prompt_template | llm 

# # Fonction utilitaire pour interroger le modèle LLM avec une question donnée.
# def query_llm(question): 
#     # La méthode 'invoke' de la chaîne LangChain exécute l'ensemble du processus
#     # (préparation du prompt + appel au LLM).
#     response = llm_chain.invoke({'question': question}) 
#     return response # Retourne la réponse brute du LLM.

# # Initialisation de l'application Flask.
# app = Flask(__name__) 

# # Définition de la route racine ('/') qui sert la page HTML principale du chatbot.
# @app.route("/") 
# def index(): 
#     # Flask cherche 'index.html' dans le dossier 'templates'.
#     return render_template("index.html") 

# # Définition de la route '/chatbot' qui gère les requêtes POST du frontend JavaScript.
# @app.route("/chatbot", methods=["POST"]) 
# def chatbot(): 
#     # Récupération des données JSON envoyées par le frontend.
#     data = request.get_json() 
#     # Extraction de la question de l'utilisateur.
#     question = data["question"] 
#     # Appel à la fonction qui interroge le chatbot (via LangChain et OpenAI).
#     response = query_llm(question) 
#     # Renvoi de la réponse du chatbot au frontend au format JSON.
#     return jsonify({"response": response}) 

# # Point d'entrée de l'application.
# # Lance le serveur Flask. 'debug=True' est utile pour le développement
# # car il redémarre le serveur automatiquement en cas de modification du code.
# if __name__ == "__main__": 
#     app.run(debug=True)




















# from flask import Flask, render_template, request, jsonify
# from langchain_openai import OpenAI
# from langchain.prompts import PromptTemplate

# prompt = open('website_text.txt', 'r').read()

# hotel_assistant_template = prompt + """
# You are the hotel manager of Landon Hotel, named "Mr. Landon". 
# Your expertise is exclusively in providing information and advice about anything related to Landon Hotel. 
# This includes any general Landon Hotel related queries. 
# You do not provide information outside of this scope. 
# If a question is not about Landon Hotel, respond with, "I can't assist you with that, sorry!" 
# Question: {question} 
# Answer: 
# """

# hotel_assistant_prompt_template = PromptTemplate( 
#     input_variables=["question"], 
#     template=hotel_assistant_template 
#     ) 

# llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0) 

# llm_chain = hotel_assistant_prompt_template | llm 

# def query_llm(question): 
#     response = llm_chain.invoke({'question': question}) 
#     return response 

# app = Flask(__name__) 

# @app.route("/") 
# def index(): 
#     return render_template("index.html") 

# @app.route("/chatbot", methods=["POST"]) 
# def chatbot(): 
#     data = request.get_json() 
#     question = data["question"] 
#     response = query_llm(question) 
#     return jsonify({"response": response}) 

# if __name__ == "__main__": 
#     app.run(debug=True)