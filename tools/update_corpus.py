import os
import sys
import glob

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.text_processor import TextProcessor

def get_epub_files(directory):
    """Scan directory for EPUB files."""
    return glob.glob(os.path.join(directory, "*.epub"))

def get_clean_filename(epub_path):
    """Generate the output filename for the cleaned text."""
    base_name = os.path.basename(epub_path)
    name_without_ext = os.path.splitext(base_name)[0]
    # Simple semantic cleanup for cleaner filenames if possible
    # e.g. "SAS - 044 - ..." -> "SAS_044_CLEAN.txt"
    # But for safety/consistency with existing pattern, we can just append _CLEAN
    # better yet, let's try to match the style "SAS_044_CLEAN.txt" manually if it matches known patterns,
    # otherwise default to "{name}_CLEAN.txt"
    
    clean_name = name_without_ext
    
    # Heuristic for SAS books based on previous manual entries
    # "SAS - 044 - ..." -> "SAS_044_CLEAN.txt"
    import re
    sas_match = re.search(r'SAS\s*[-_]?\s*(\d+)', name_without_ext, re.IGNORECASE)
    if sas_match:
        number = sas_match.group(1).zfill(3)
        clean_name = f"SAS_{number}"
    
    return os.path.join(os.path.dirname(epub_path), f"{clean_name}_CLEAN.txt")

def update_corpus(directory):
    print(f"🔍 Scanning {directory} for EPUBs...")
    epubs = get_epub_files(directory)
    
    if not epubs:
        print("❌ No EPUB files found.")
        return

    print(f"📚 Found {len(epubs)} EPUBs.")
    
    new_count = 0
    skipped_count = 0
    
    for epub_path in epubs:
        output_file = get_clean_filename(epub_path)
        
        if os.path.exists(output_file):
            skipped_count += 1
            # print(f"⏩ Skipping {os.path.basename(epub_path)} (Clean file exists: {os.path.basename(output_file)})")
            continue

        print(f"📖 Processing NEW book: {os.path.basename(epub_path)} -> {os.path.basename(output_file)}...")
        try:
            # Extract
            raw_text = TextProcessor.extract_from_epub(epub_path)
            
            # Normalize
            clean_text = TextProcessor.normalize_whitespace(raw_text)
            
            # Save
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            
            stats = TextProcessor.get_stats(clean_text)
            print(f"✅ Created {os.path.basename(output_file)}")
            print(f"   📊 {stats['words']} words, {stats['suspect_words']} suspect words")
            new_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(epub_path)}: {e}")

    print("\n" + "="*40)
    print(f"✨ Corpus Update Complete.")
    print(f"➕ Added: {new_count}")
    print(f"⏩ Skipped (already exist): {skipped_count}")
    print("="*40)

if __name__ == "__main__":
    # Target the root directory of the project (parent of tools/)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    update_corpus(root_dir)
