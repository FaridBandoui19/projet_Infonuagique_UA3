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
        # 1. Services & équipements
        (["service","commodit","amenit","équipement"],
         ["OUR SERVICES & AMENITIES","OUR SERVICES","AMENITIES"]),
        
        # 2. Logo / identité visuelle
        (["logo","logotype","logomark","marque"],
         ["LOGO SYSTEM","OUR LOGO","LOGOTYPE","OUR LOGOTYPE",
          "LOGOMARK","OUR LOGOMARK","LOGO LOCK-UP","LOGO USAGE",
          "SECONDARY SUBMARKS","LOGO COMPONENTS & CONSTRUCTION"]),
        
        # 3. Couleurs
        (["couleur","color"],
         ["COLOR SYSTEM","OUR COLORS","COLOR CODES","BACKGROUND COLORS",
          "WEB ACCESSIBLE COLORS","COLOR USAGE"]),
        
        # 4. Graphiques / icônes / motifs / bannières
        (["graphique","icône","icone","pattern","motif","bannière","banniere"],
         ["SUPPORTING GRAPHICS","OUR ICONS","OUR PATTERNS","BANNER GRAPHIC"]),
         
         # 5. Photographie
        (["photo","photograph"],["PHOTOGRAPHY","STYLE","COMPOSITION","LIGHTING","COLOR"]),
        
        # 6. Valeurs / mission / vision / slogan
        (["valeur","mission","vision","slogan","purpose"],
         ["OUR VALUES","MISSION STATEMENT","VISION STATEMENT","OUR SLOGAN","BRAND FOUNDATION"]),
        
         # 7. Matériel imprimé / documents
        (["papier","facture","newsletter","sales sheet","stationery","devis","invoice"],
         ["BRANDED MATERIALS","STATIONERY","NEWSLETTER","INVOICE","SALES SHEET"]),
        
        # 8. Typographie
        (["typographie", "typo", "font", "fonts", "police", "polices"],
        ["TYPOGRAPHY SYSTEM", "OUR PRIMARY TYPEFACE", "OUR ACCENT TYPEFACE", "TYPOGRAPHY USAGE"]),

        # 9. Personnalité de marque
        (["personnalité", "personnalite", "brand personality", "personality"],
        ["OUR BRAND PERSONALITY", "BRAND CHARACTERISTICS"]),

        # 10. Voix & ton
        (["voix", "ton", "tone", "voice", "style verbal", "style d'écriture", "style d'ecriture", "style ecriture"],
        ["OUR VOICE & TONE", "OUR VERBAL STYLE"]),

        # 11. Style visuel (look & feel)
        (["look", "feel", "style visuel", "visuel", "apparence"],
        ["OUR LOOK & FEEL", "OUR VISUAL STYLE"]),

        # 12. Clients / cible
        (["client", "clients", "customer", "customers", "cible", "audience"],
        ["OUR CUSTOMERS"]),

        # 13. Localisation
        (["localisation", "emplacement", "où", "ou", "situé", "situe", "adresse", "quartier",
        "lieu", "location", "située", "situee", "se trouve"],
        ["WEST END, LONDON", "The Landon Hotel – West End", "123 Oxford Street", "LOCAL SIGHTS"]),

        # 14. Tarification / prix
        (["tarif", "tarifs", "tarification", "prix", "coût", "cout", "frais",
        "combien", "price", "prices", "pricing", "rate", "rates", "fee", "fees"],
        ["INVOICE", "NEWSLETTER & INVOICE", "Room Charge", "Room Tax", "Occupancy Tax"]),
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
