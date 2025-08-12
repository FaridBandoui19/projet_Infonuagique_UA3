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

