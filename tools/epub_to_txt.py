
import sys
import os
from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def epub_to_txt(epub_path):
    if not os.path.exists(epub_path):
        print(f"Error: File not found: {epub_path}")
        return

    output_path = os.path.splitext(epub_path)[0] + ".txt"
    
    print(f"Converting {epub_path} to {output_path}...")
    
    try:
        book = epub.read_epub(epub_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text('\n')
                    
                    # Basic cleaning of multiple newlines
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    clean_text = '\n'.join(lines)
                    
                    if clean_text:
                        f.write(clean_text + "\n\n")
                        
        print(f"✅ Conversion complete: {output_path}")
        
    except Exception as e:
        print(f"❌ Error converting EPUB: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python epub_to_txt.py <epub_path>")
        sys.exit(1)
        
    epub_to_txt(sys.argv[1])
