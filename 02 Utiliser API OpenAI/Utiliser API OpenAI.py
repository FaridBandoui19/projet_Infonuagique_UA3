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









# # Version 03

# # 02 Utiliser API OpenAI.py
# import os
# from dotenv import load_dotenv
# from openai import OpenAI, RateLimitError
# from tenacity import retry, wait_exponential, stop_after_attempt

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise RuntimeError("OPENAI_API_KEY manquante. Ajoute-la dans le fichier .env")

# client = OpenAI()

# def is_quota_error(e: Exception) -> bool:
#     return "insufficient_quota" in str(e).lower() or "quota" in str(e).lower()

# @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
# def call_openai(messages):
#     try:
#         return client.chat.completions.create(
#             model="gpt-4o-mini",
#             temperature=0.2,
#             messages=messages,
#         )
#     except RateLimitError as e:
#         # Ne pas réessayer si c’est un manque de crédits
#         if is_quota_error(e):
#             raise
#         # Sinon, laisser tenacity réessayer (rate limit momentané)
#         raise

# prompt = "You will be provided with a block of text, and your task is to extract a list of keywords from it."
# text = "The earliest successful AI program was written in 1951 by Christopher Strachey..."

# try:
#     resp = call_openai([
#         {"role": "system", "content": prompt},
#         {"role": "user", "content": text},
#     ])
#     print("✓ API OK")
#     print(resp.choices[0].message.content)

# except RateLimitError as e:
#     if is_quota_error(e):
#         print("❌ Crédits API insuffisants. Ajoute des crédits dans Billing > Buy credits.")
#     else:
#         print("❌ Trop de requêtes. Réessaie dans un instant.")
# except Exception as e:
#     print("❌ Erreur:", e)



# # Version 02

# # 02 Utiliser API OpenAI.py
# import os
# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise RuntimeError("OPENAI_API_KEY manquante. Ajoute-la dans le fichier .env")

# client = OpenAI()

# # Test simple : extraction de mots-clés
# prompt = (
#     "You will be provided with a block of text, "
#     "and your task is to extract a list of keywords from it."
# )
# text = (
#     "The earliest successful AI program was written in 1951 by Christopher Strachey..."
# )

# resp = client.chat.completions.create(
#     model="gpt-4o-mini",
#     temperature=0.2,
#     messages=[
#         {"role": "system", "content": prompt},
#         {"role": "user", "content": text},
#     ],
# )

# print("✓ API OK")
# print(resp.choices[0].message.content)





# # Version 01

# from openai import OpenAI
# client = OpenAI()

# response = client.chat.completions.create(
#   model="gpt-4o-mini",
#   messages=[
#     {
#       "role": "system",
#       "content": "You will be provided with a block of text, and your task is to extract a list of keywords from it."
#     },
#     {
#       "role": "user",
#       "content": "The earliest successful AI program was written in 1951 by Christopher Strachey, later director of the Programming Research Group at the University of Oxford. Strachey’s checkers (draughts) program ran on the Ferranti Mark I computer at the University of Manchester, England. By the summer of 1952 this program could play a complete game of checkers at a reasonable speed. Information about the earliest successful demonstration of machine learning was published in 1952. Shopper, written by Anthony Oettinger at the University of Cambridge, ran on the EDSAC computer. Shopper’s simulated world was a mall of eight shops. When instructed to purchase an item, Shopper would search for it, visiting shops at random until the item was found. While searching, Shopper would memorize a few of the items stocked in each shop visited (just as a human shopper might). The next time Shopper was sent out for the same item, or for some other item that it had already located, it would go to the right shop straight away. This simple form of learning, as is pointed out in the introductory section What is intelligence?, is called rote learning. The first AI program to run in the United States also was a checkers program, written in 1952 by Arthur Samuel for the prototype of the IBM 701. Samuel took over the essentials of Strachey’s checkers program and over a period of years considerably extended it. In 1955 he added features that enabled the program to learn from experience. Samuel included mechanisms for both rote learning and generalization, enhancements that eventually led to his program’s winning one game against a former Connecticut checkers champion in 1962."
#     }
#   ],
#   temperature=0.5
# )

# print(response.choices[0].message.content)