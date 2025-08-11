# Version 04

# 01_collecte_pdf.py
import sys
from pathlib import Path
import fitz  # PyMuPDF

# --- chemins ---
ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "Landon-Hotel.pdf"        # mets ton PDF ici (même dossier que ce script)
OUT_PATH = ROOT / "pdf_text.txt"            # sortie attendue

def extract_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        parts.append(page.get_text("text"))
    doc.close()
    return "\n".join(parts)

def main():
    if not PDF_PATH.exists():
        print(f"❌ PDF introuvable : {PDF_PATH}")
        print("   ➜ Vérifie le nom/chemin du fichier ou modifie PDF_PATH.")
        sys.exit(1)

    print(f"📄 Lecture : {PDF_PATH}")
    text = extract_text_from_pdf(PDF_PATH)

    # Petit garde-fou si le PDF est vide ou scanné (sans texte)
    if not text.strip():
        print("⚠️  Aucun texte extrait. Le PDF est peut-être scanné (images).")
        print("   ➜ On pourra ajouter l’OCR plus tard si besoin.")
    else:
        OUT_PATH.write_text(text, encoding="utf-8")
        print(f"✅ Extraction OK → {OUT_PATH}")
        print(f"   Caractères : {len(text):,}")
        # Aperçu
        preview = text.strip().splitlines()
        print("--- APERÇU ---")
        print("\n".join(preview[:10]))  # affiche ~10 premières lignes

if __name__ == "__main__":
    main()


















# 
# # 01 Collecte et préparation des données PDF.py
# import fitz  # PyMuPDF
# import os

# PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "Landon-Hotel.pdf")
# OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "pdf_text.txt")

# def extract_text_from_pdf(pdf_file_path: str) -> str:
#     doc = fitz.open(pdf_file_path)
#     parts = []
#     for page_num in range(doc.page_count):
#         page = doc.load_page(page_num)
#         parts.append(page.get_text("text"))
#     doc.close()
#     return "\n".join(parts)

# if __name__ == "__main__":
#     pdf_abs = os.path.abspath(PDF_PATH)
#     out_abs = os.path.abspath(OUT_PATH)

#     if not os.path.exists(pdf_abs):
#         raise FileNotFoundError(f"PDF introuvable : {pdf_abs}")

#     text = extract_text_from_pdf(pdf_abs)
#     with open(out_abs, "w", encoding="utf-8") as f:
#         f.write(text)

#     print("✓ Extraction terminée")
#     print(f"→ {out_abs}")
#     print(f"Caractères: {len(text):,}")



# import fitz

# def extract_text_from_pdf(pdf_file_path):
#     try:
#         doc = fitz.open(pdf_file_path)
#         pdf_text = ""
#         for page_num in range(doc.page_count):
#             page = doc.load_page(page_num)
#             pdf_text += page.get_text("text")
#         doc.close()
#         return pdf_text
#     except Exception as e:
#         return f"Error extracting text: {e}"

# pdf_path = "C:\\Users\\hp\\OneDrive - Collège la Cité\\00Semestre 02\\003 Outils Infonuagique\\Partie 3\\Projet 1\\Projet AI chatbot\\Projet AI chatbot\\Collecte et préparation des données PDF\\Landon-Hotel.pdf"
# extracted_text = extract_text_from_pdf(pdf_path)

# file = open("pdf_text.txt", "w", encoding='utf-8')
# file.write(extracted_text)



# # Version 02
# import fitz

# def extract_text_from_pdf(pdf_file_path):
#     try:
#         doc = fitz.open(pdf_file_path)
#         pdf_text = ""
#         for page_num in range(doc.page_count):
#             page = doc.load_page(page_num)
#             pdf_text += page.get_text("text")
#         doc.close()
#         return pdf_text
#     except Exception as e:
#         return f"Error extracting text: {e}"

# # 🎯 chemin où ce trouve le fichier PDF a lire
# pdf_path = "C:\\Users\\hp\\OneDrive - Collège la Cité\\00Semestre 02\\003 Outils Infonuagique\\Partie 3\\Projet 1\\Projet AI chatbot\\Projet AI chatbot\\Collecte et préparation des données PDF\\Landon-Hotel.pdf"
# extracted_text = extract_text_from_pdf(pdf_path)

# # Assurez-vous que le fichier de sortie a bien l'extension .txt
# # Et qu'il est écrit dans un emplacement où vous avez les permissions
# file = open("pdf_text.txt", "w", encoding='utf-8')
# file.write(extracted_text)