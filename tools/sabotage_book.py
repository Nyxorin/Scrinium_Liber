
import os
import sys
import random
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.saboteur import Saboteur
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore")

def extract_text_from_epub(epub_path, char_limit=60000): # ~30 pages
    book = epub.read_epub(epub_path)
    full_text = []
    total_chars = 0
    
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text()
            full_text.append(text)
            total_chars += len(text)
            if total_chars >= char_limit:
                break
                
    return "\n".join(full_text)[:char_limit]

def sabotage_text(text):
    saboteur = Saboteur() # We don't need the LLM for Visual Noise, just the methods
    
    lines = text.split('\n')
    sabotaged_lines = []
    
    print("😈 Sabotaging text... This may take a moment.")
    
    error_count = 0
    
    for line in lines:
        if len(line.strip()) < 10:
            sabotaged_lines.append(line)
            continue
            
        # Apply visual noise aggressively
        # We run it multiple times to ensure high error rate
        dirty_line = line
        
        # 1. Visual Swaps (Higher prob)
        if random.random() < 0.7:
             dirty_line = saboteur._visual_swap(dirty_line)
             error_count += 1
             
        # 2. Drop Accents
        if random.random() < 0.5:
             dirty_line = saboteur._drop_diacritics(dirty_line)
             error_count += 1
             
        # 3. Punctuation Noise
        if random.random() < 0.3:
             dirty_line = saboteur._punct_noise(dirty_line)
             error_count += 1
             
        # 4. Glued Words (Very annoying)
        if random.random() < 0.2:
             dirty_line = saboteur._glue_words(dirty_line)
             error_count += 1
             
        sabotaged_lines.append(dirty_line)
        
    print(f"💀 Damage Report: ~{error_count} corruption events applied.")
    return "\n".join(sabotaged_lines)

if __name__ == "__main__":
    epub_path = "Villiers,Gérard de [SAS-006] Dossier Kennedy (1967) Espionnage .A.epub"
    if not os.path.exists(epub_path):
        print("File not found!")
        sys.exit(1)
        
    print(f"📖 Reading {epub_path}...")
    clean_text = extract_text_from_epub(epub_path)
    
    with open("SAS_006_CLEAN.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)
    print("✅ Ground Truth saved to SAS_006_CLEAN.txt")
    
    dirty_text = sabotage_text(clean_text)
    
    output_path = "SAS_006_SABOTAGED.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(dirty_text)
        
    print(f"✅ Sabotaged text saved to {output_path}")
    print("Sample:\n" + dirty_text[:500])
