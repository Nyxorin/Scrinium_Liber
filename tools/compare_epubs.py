import zipfile
import sys
import re
import difflib
from bs4 import BeautifulSoup

def extract_text_from_epub(epub_path, max_chapters=5):
    text_content = {}
    try:
        with zipfile.ZipFile(epub_path, 'r') as z:
            # Find HTML files
            html_files = [f for f in z.namelist() if f.endswith(('.html', '.xhtml'))]
            html_files.sort() # Simple sort, hopefully follows chapter order
            
            count = 0
            for f in html_files:
                if count >= max_chapters: break
                if 'cover' in f.lower() or 'nav' in f.lower() or 'toc' in f.lower(): continue
                
                with z.open(f) as html_file:
                    soup = BeautifulSoup(html_file.read(), 'html.parser')
                    text_content[f] = soup.get_text()
                    count += 1
    except Exception as e:
        print(f"Error reading {epub_path}: {e}")
        return {}
    return text_content

def compare_texts(original_path, cleaned_path):
    print(f"Comparing:")
    print(f"Original: {original_path}")
    print(f"Cleaned:  {cleaned_path}")
    print("-" * 50)
    
    orig_texts = extract_text_from_epub(original_path)
    clean_texts = extract_text_from_epub(cleaned_path)
    
    # Try to match files by name if possible, or just sequential
    # Since cleaning might rename files (unlikely but possible), likely same names
    
    changes_found = 0
    
    for filename, orig_text in orig_texts.items():
        if filename in clean_texts:
            clean_text = clean_texts[filename]
            
            # Normalize whitespace
            orig_lines = [l.strip() for l in orig_text.splitlines() if l.strip()]
            clean_lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
            
            diff = difflib.unified_diff(orig_lines, clean_lines, n=0, lineterm='')
            
            file_changes = list(diff)
            if file_changes:
                print(f"CHANGES IN {filename}:")
                for line in file_changes:
                    if line.startswith('---') or line.startswith('+++') or line.startswith('@@'): continue
                    print(line)
                changes_found += len(file_changes)
                print("\n")
                
    if changes_found == 0:
        print("No differences found in the first few chapters.")
    else:
        print(f"Total differences sections found: {changes_found}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_epubs.py <original_epub> <cleaned_epub>")
    else:
        compare_texts(sys.argv[1], sys.argv[2])
