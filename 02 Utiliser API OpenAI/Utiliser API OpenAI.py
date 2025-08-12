# Version 04

# 02_test_llm_sur_pdf.py
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import os, sys

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY manquante dans .env")

# --- Résolution du chemin de pdf_text.txt ---
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent  # ex: .../Projet AI chatbot
CLI = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
ENV = Path(os.getenv("PDF_TEXT_PATH")).resolve() if os.getenv("PDF_TEXT_PATH") else None

CANDIDATES = [
    CLI,
    ENV,
    PROJECT / "pdf_text.txt",
    PROJECT / "01 Collecte et préparation des données PDF" / "pdf_text.txt",
    HERE / "pdf_text.txt",
    Path.cwd() / "pdf_text.txt",
]

TXT_PATH = next((p for p in CANDIDATES if p and p.exists()), None)
if not TXT_PATH:
    tried = [str(p) for p in CANDIDATES if p]
    raise FileNotFoundError("Impossible de trouver pdf_text.txt. Essais :\n- " + "\n- ".join(tried))

print(f"📄 Contexte: {TXT_PATH}")
text = TXT_PATH.read_text(encoding="utf-8")

def pick_context(question: str, doc: str, max_chars: int = 4000) -> str:
    q = (question or "").lower()
    keys = []
    if "service" in q or "équipement" in q or "amenit" in q:
        keys = ["OUR SERVICES", "AMENITIES"]
    elif "logo" in q:
        keys = ["LOGO SYSTEM", "OUR LOGO", "LOGO"]
    elif "couleur" in q or "color" in q:
        keys = ["COLOR SYSTEM", "OUR COLORS"]
    elif "typograph" in q or "police" in q or "font" in q:
        keys = ["TYPOGRAPHY SYSTEM", "OUR PRIMARY TYPEFACE", "OUR ACCENT TYPEFACE"]
    elif "valeur" in q or "slogan" in q or "mission" in q or "vision" in q:
        keys = ["OUR VALUES", "OUR SLOGAN", "MISSION STATEMENT", "VISION STATEMENT"]

    if keys:
        up = doc.upper()
        for k in keys:
            i = up.find(k)
            if i != -1:
                start = max(0, i - max_chars // 4)
                end = min(len(doc), i + max_chars // 2)
                return doc[start:end]
    return doc[:max_chars]

client = OpenAI()

def ask(question: str) -> str:
    ctx = pick_context(question, text)
    system_msg = (
        "Tu es 'Mr. Landon', manager du Landon Hotel. "
        "Réponds UNIQUEMENT avec les infos du CONTEXTE fourni. "
        "Si l'info manque, dis-le poliment et propose un sujet Landon proche."
    )
    user_msg = f"CONTEXTE:\n{ctx}\n\nQUESTION:\n{question}"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    print("Test 1) Bonjour")
    print(ask("Bonjour"))
    print("\nTest 2) Quels sont vos services ?")
    print(ask("Quels sont vos services ?"))
