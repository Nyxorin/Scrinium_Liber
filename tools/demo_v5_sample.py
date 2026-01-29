
import sys
import os
from ebooklib import epub
from bs4 import BeautifulSoup

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from correctors.semantic_corrector import SemanticCorrector
from core.text_processor import TextProcessor

print("--- DEMO V5 : ECHANTILLON ---")

# Chargement
epub_path = "livres_corriges/SAS_047_SMART_CLEAN_V2.epub"
book = epub.read_epub(epub_path)
semantic = SemanticCorrector()

# Extraction 1er chapitre
for item in book.get_items():
    if item.get_type() == 9: # ITEM_DOCUMENT
        content = item.get_content().decode('utf-8')
        raw_text = TextProcessor.extract_from_html(content)
        
        # On prend un échantillon de 2000 caractères
        sample = raw_text[:2000]
        lines = sample.split('\n')
        
        print(f"\n📄 Analyse de l'échantillon ({len(lines)} lignes)...\n")
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Correction Sémantique V5
            corrected = semantic.correct_segment(line)
            
            if line != corrected:
                print(f"🔴 AVANT: {line}")
                print(f"🟢 APRES: {corrected}")
                print("-" * 40)
            else:
                # On affiche aussi quelques lignes inchangées pour contexte
                if len(line) > 50:
                    print(f"⚪ STET : {line[:60]}...")
        
        break
