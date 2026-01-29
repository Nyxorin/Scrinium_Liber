import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.text_processor import TextProcessor

# List of new books to process
books = [
    ("bloy_leon_-_exegese_des_lieux_communs.epub", "BLOY_Exegese_CLEAN.txt"),
    ("Exbrayat, Charles - [Imogène 5] Notre Imogène.epub", "EXBRAYAT_Imogene5_CLEAN.txt"),
    ("Exbrayat, Charles - [Imogène 1] Ne vous fachez pas Imogène.epub", "EXBRAYAT_Imogene1_CLEAN.txt"),
    ("Exbrayat, Charles - [Imogène 2] Imogène est de retour.epub", "EXBRAYAT_Imogene2_CLEAN.txt"),
    ("Exbrayat, Charles - [Imogène 3] Encore vous Imogene.epub", "EXBRAYAT_Imogene3_CLEAN.txt"),
    ("Exbrayat, Charles - [Imogène 4] Imogene, Vous etes Impossible !.epub", "EXBRAYAT_Imogene4_CLEAN.txt"),
    ("Exbrayat, Charles - [Imogène 6] Les fiancailles d'Imogène.epub", "EXBRAYAT_Imogene6_CLEAN.txt")
]

print("📚 Literary Corpus Extraction (Bloy & Exbrayat)...")

for epub_file, output_file in books:
    if os.path.exists(output_file):
        print(f"⏩ Skipping {output_file} (Already exists)")
        continue
        
    if not os.path.exists(epub_file):
        print(f"⚠️ Warning: {epub_file} not found!")
        continue

    print(f"📖 Processing {epub_file} -> {output_file}...")
    try:
        # Extract
        raw_text = TextProcessor.extract_from_epub(epub_file)
        
        # Normalize
        clean_text = TextProcessor.normalize_whitespace(raw_text)
        
        # Remove empty lines that clutter
        lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
        clean_text = "\n".join(lines)

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)
            
        print(f"✅ Saved {output_file} ({len(clean_text)} chars)")
        
    except Exception as e:
        print(f"❌ Error processing {epub_file}: {e}")

print("✨ Literary Extraction Complete.")
