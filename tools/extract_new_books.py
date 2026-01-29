import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.text_processor import TextProcessor

# List of new books to process
books = [
    ("SAS - 044 - Meurtre a Athènes - Gérard De Villiers copie.epub", "SAS_044_CLEAN.txt"),
    ("SAS 079 - Chasse à l'homme au Pérou, Plon Pressesà l'homme au Pérou, Plon Presses de la Cité, 1985 copie.epub", "SAS_079_CLEAN.txt"),
    ("SAS 106 Le disparu des Canaries - Gérard De Villiers copie.epub", "SAS_106_CLEAN.txt"),
    ("SAS 114 - L'Or de Moscou, Éditions Gérard de VillL'Or de Moscou, Éditions Gérard de Villiers, 1994 copie.epub", "SAS_114_CLEAN.txt"),
    ("SAS 115 - Les croisés de l'Apartheid- Éditions Gérard de Villiers - 1994 - inconnu copie.epub", "SAS_115_CLEAN.txt"),
    ("SAS 117 - Tuerie à Marrakech, Éditions Gérard de ie à Marrakech, Éditions Gérard de Villiers, 1995 copie.epub", "SAS_117_CLEAN.txt")
]

print("📚 Bulk Extraction Started...")

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
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)
            
        print(f"✅ Saved {output_file} ({len(clean_text)} chars)")
        
    except Exception as e:
        print(f"❌ Error processing {epub_file}: {e}")

print("✨ Bulk Extraction Complete.")
