#!/usr/bin/env python3
"""
Audit Global des mots inconnus.
Scanne un EPUB et génère un rapport des mots non trouvés dans le dictionnaire/whitelist.
Permet d'identifier les fautes systémiques (ex: 'Sommalie', 'lhomme').
"""

import sys
import collections
import json
import re
from pathlib import Path
from ebooklib import epub
import ebooklib

# Ajout du chemin racine pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from core.dictionary import FrenchDictionary
from core.text_processor import TextProcessor

def audit_book(epub_path, output_report):
    print(f"📖 Audit de : {epub_path}")
    
    try:
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"❌ Erreur lecture EPUB: {e}")
        return

    dictionary = FrenchDictionary()
    # Chargement whitelist manuel direct pour être sûr
    whitelist_path = Path("data/knowledge/whitelist.json")
    whitelist = set()
    if whitelist_path.exists():
        with open(whitelist_path, 'r') as f:
            whitelist = set(word.lower() for word in json.load(f))
            print(f"✅ Whitelist chargée ({len(whitelist)} mots)")

    unknown_counter = collections.Counter()
    total_words = 0
    
    # Regex pour découper les mots (très basique pour l'audit)
    word_pattern = re.compile(r"\b\w+\b")

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode('utf-8')
            text = TextProcessor.extract_from_html(content)
            
            # Nettoyage basique pour l'analyse
            words = word_pattern.findall(text)
            
            for word in words:
                if len(word) < 2: continue # Ignorer lettres seules, sauf 'y', 'a'... on simplifie
                if word.isdigit(): continue
                
                total_words += 1
                
                word_lower = word.lower()
                
                # 1. Check Whitelist
                if word_lower in whitelist:
                    continue
                
                # 2. Check Dictionary
                if dictionary.validate(word):
                    continue
                
                # C'est un inconnu
                unknown_counter[word] += 1

    print(f"\n📊 Analyse terminée : {total_words} mots scannés.")
    print(f"🚩 {len(unknown_counter)} mots uniques inconnus trouvés.")

    # Export Top 100
    top_unknowns = unknown_counter.most_common(200)
    
    report = {
        "epub": epub_path,
        "total_unknown_unique": len(unknown_counter),
        "top_200": [{"word": w, "count": c} for w, c in top_unknowns]
    }
    
    with open(output_report, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"💾 Rapport sauvegardé : {output_report}")
    
    # Affichage terminal des Top 20
    print("\n🏆 Top 20 Inconnus (Candidats à correction/whitelist) :")
    for w, c in top_unknowns[:20]:
        print(f"   - {w} ({c})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/audit_unknown_words.py <input.epub> <report.json>")
        sys.exit(1)
        
    audit_book(sys.argv[1], sys.argv[2])
