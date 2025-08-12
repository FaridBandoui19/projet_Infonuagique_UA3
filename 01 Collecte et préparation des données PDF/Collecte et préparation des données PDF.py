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
