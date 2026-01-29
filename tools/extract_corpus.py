
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.text_processor import TextProcessor

def extract_and_save(epub_path, output_filename):
    print(f"📖 Extractions de {epub_path}...")
    try:
        if not os.path.exists(epub_path):
            print(f"❌ Erreur: Le fichier {epub_path} n'existe pas.")
            return False
            
        # Extraction brute
        raw_text = TextProcessor.extract_from_epub(epub_path)
        
        # Nettoyage de base (espaces, sauts de ligne)
        clean_text = TextProcessor.normalize_whitespace(raw_text)
        
        # Sauvegarde
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(clean_text)
            
        stats = TextProcessor.get_stats(clean_text)
        print(f"✅ Sauvegardé dans {output_filename}")
        print(f"📊 Stats: {stats['words']} mots, {stats['suspect_words']} mots suspects.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction de {epub_path}: {e}")
        return False

if __name__ == "__main__":
    books = [
        {
            "in": "Villiers,Gérard de [SAS-011] Magie noire à New York (1968) Espionnage .A.epub",
            "out": "SAS_011_CLEAN.txt"
        },
        {
            "in": "Villiers,Gérard de [SAS-005] Rendez-vous à San Francisco (1966) french.Alex.epub",
            "out": "SAS_005_CLEAN.txt"
        }
    ]
    
    for book in books:
        extract_and_save(book["in"], book["out"])
