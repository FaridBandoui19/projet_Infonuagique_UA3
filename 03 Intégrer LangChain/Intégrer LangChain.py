# 03 Intégrer LangChain/Intégrer LangChain.py
from dotenv import load_dotenv
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# --- Chargement de la clé depuis .env ---
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY manquante dans .env")

# --- Localiser pdf_text.txt (cherche dans plusieurs endroits courants) ---
ROOT = Path(__file__).resolve().parents[1]  # racine du projet (dossier "Projet AI chatbot")
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

# --- Sélecteur de contexte: prend un extrait pertinent en fonction de la question ---
def select_context(question: str, doc: str, max_chars: int = 15000) -> str:
    """
    Retourne un extrait pertinent du doc en fonction de la question.
    Amélioration: pour la typographie, on concatène 3 blocs (Primary / Accent / Usage).
    """
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

    # --- Cas typographie : on assemble plusieurs sections ---
    if any(k in q for k in ["typograph", "police", "font", "typo"]):
        anchors = [
            "TYPOGRAPHY SYSTEM",
            "OUR PRIMARY TYPEFACE",
            "BRANDON GROTESQUE",
            "OUR ACCENT TYPEFACE",
            "ESSONNES",
            "TYPOGRAPHY USAGE",
        ]
        parts = []
        for a in anchors:
            idx = find_idx(a)
            chunk = slice_around(idx)
            if chunk:
                parts.append(chunk)
        if parts:
            joined = "\n\n---\n\n".join(parts)
            # borne de sécurité si très long
            return joined[:max_chars]

    # --- Thèmes généraux (services, logo, couleurs, etc.) ---
    themes = [
        (["service", "commodit", "amenit", "équipement"], [
            "OUR SERVICES & AMENITIES", "OUR SERVICES", "AMENITIES"
        ]),
        (["logo", "logotype", "logomark", "marque"], [
            "LOGO SYSTEM", "OUR LOGO", "LOGOTYPE", "OUR LOGOTYPE",
            "LOGOMARK", "OUR LOGOMARK", "LOGO LOCK-UP", "LOGO USAGE",
            "SECONDARY SUBMARKS", "LOGO COMPONENTS & CONSTRUCTION"
        ]),
        (["couleur", "color"], [
            "COLOR SYSTEM", "OUR COLORS", "COLOR CODES", "BACKGROUND COLORS",
            "WEB ACCESSIBLE COLORS", "COLOR USAGE"
        ]),
        (["graphique", "icône", "icone", "pattern", "motif", "bannière", "banniere"], [
            "SUPPORTING GRAPHICS", "OUR ICONS", "OUR PATTERNS", "BANNER GRAPHIC"
        ]),
        (["photo", "photograph"], [
            "PHOTOGRAPHY", "STYLE", "COMPOSITION", "LIGHTING", "COLOR"
        ]),
        (["valeur", "mission", "vision", "slogan", "purpose"], [
            "OUR VALUES", "MISSION STATEMENT", "VISION STATEMENT",
            "OUR SLOGAN", "BRAND FOUNDATION"
        ]),
        (["papier", "facture", "newsletter", "sales sheet", "stationery", "devis", "invoice"], [
            "BRANDED MATERIALS", "STATIONERY", "NEWSLETTER", "INVOICE", "SALES SHEET"
        ]),
    ]

    def first_anchor_idx(anchors):
        for a in anchors:
            i = find_idx(a)
            if i != -1:
                return i
        return -1

    for keys, anchors in themes:
        if any(k in q for k in keys):
            i = first_anchor_idx(anchors)
            if i != -1:
                return slice_around(i, before=max_chars // 4, after=max_chars // 2)

    # Fallbacks
    for fb in ["BRANDON GROTESQUE", "OUR COLORS", "OUR SERVICES", "PHOTOGRAPHY"]:
        i = find_idx(fb)
        if i != -1:
            return slice_around(i, before=max_chars // 4, after=max_chars // 2)

    return doc[:max_chars]


# --- Règles système (tes règles, en message system) ---
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
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_rules),
    ("user", "CONTEXTE:\n{context}\n\nQUESTION:\n{question}")
])

# --- Modèle OpenAI via LangChain ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm  # LCEL: prompt → LLM

def ask(question: str) -> str:
    ctx = select_context(question, FULL_DOC)
    resp = chain.invoke({"context": ctx, "question": question})
    return getattr(resp, "content", str(resp))

if __name__ == "__main__":
    print(f"(Contexte chargé depuis) {TXT_PATH}")
    print("\nQ: Bonjour")
    print("A:", ask("Bonjour"))
    print("\nQ: Quels sont vos services ?")
    print("A:", ask("Quels sont vos services ?"))
    print("\nQ: Parle-moi de la typographie")
    print("A:", ask("Parle-moi de la typographie"))





# # Version 03

# # 03 Intégrer LangChain.py
# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate

# load_dotenv()
# if not os.getenv("OPENAI_API_KEY"):
#     raise RuntimeError("OPENAI_API_KEY manquante dans .env")

# # Lire le contexte (le PDF en texte)
# with open(os.path.join(os.path.dirname(__file__), "..", "pdf_text.txt"), "r", encoding="utf-8") as f:
#     context = f.read()

# # (Option simple) limiter la taille du contexte pour éviter des 429
# context = context[:4000]

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

# tmpl = PromptTemplate(input_variables=["question"], template=hotel_assistant_template)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# chain = tmpl | llm

# def ask(q: str) -> str:
#     resp = chain.invoke({"question": q})
#     return resp.content if hasattr(resp, "content") else str(resp)

# if __name__ == "__main__":
#     print("Q: Bonjour")
#     print("A:", ask("Bonjour"))
#     print("Q: Quels sont vos services ?")
#     print("A:", ask("Quels sont vos services ?"))



# Version 01
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
#     print(llm_chain.invoke({'question': question})) 

# while True:
#     query_llm(input())




# # Version 02
# from langchain_openai import OpenAI
# from langchain.prompts import PromptTemplate

# # 🎯 IMPORTANT : Assurez-vous que 'pdf_text.txt' est le fichier que vous lisez
# # Cette ligne lit le contenu de votre PDF extrait pour l'intégrer dans le prompt du chatbot.
# prompt = open('pdf_text.txt', 'r', encoding='utf-8').read() 

# # Le gabarit du prompt qui définit la personnalité et les règles du chatbot.
# # Il inclut le texte du PDF ({prompt}) comme base de connaissances.
# hotel_assistant_template = prompt + """
# You are the hotel manager of Landon Hotel, named "Mr. Landon". 
# Your expertise is exclusively in providing information and advice about anything related to Landon Hotel. 
# This includes any general Landon Hotel related queries. 
# You do not provide information outside of this scope. 
# If a question is not about Landon Hotel, respond with, "I can't assist you with that, sorry!" 
# Question: {question} 
# Answer: 
# """


# # Création de l'objet PromptTemplate qui utilise 'question' comme variable d'entrée.
# hotel_assistant_prompt_template = PromptTemplate( 
#     input_variables=["question"], 
#     template=hotel_assistant_template 
# ) 

# # Initialisation du modèle OpenAI.
# # 🚀 Vous pouvez changer le modèle ici pour une version plus récente de GPT-4.
# # Par exemple, 'gpt-4o-mini' pour une bonne performance/coût, ou 'gpt-4-turbo-preview' pour plus de puissance.
# llm = OpenAI(model='gpt-4o-mini', temperature=0) 

# # Création de la chaîne LangChain : la sortie du PromptTemplate est envoyée au modèle LLM.
# llm_chain = hotel_assistant_prompt_template | llm 

# # Fonction pour interroger le chatbot. Elle exécute la chaîne LangChain.
# def query_llm(question): 
#     # La fonction invoke exécute la chaîne LangChain avec la question de l'utilisateur
#     response = llm_chain.invoke({'question': question}) 
#     return response # Retourne la réponse pour le déploiement web

# # La boucle 'while True' est commentée car elle est remplacée par l'intégration Flask
# # pour l'interface web.
# # while True:
# #     user_input = input("Posez votre question: ")
# #     print(query_llm(user_input))