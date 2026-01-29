#!/usr/bin/env python3
"""
Lecteur EPUB CLI pour Scrinium Liber.
Permet d'inspecter rapidement le contenu textuel d'un EPUB sans quitter le terminal.
"""

import sys
import argparse
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import textwrap

def list_chapters(book):
    """Affiche la liste des documents (chapitres) de l'EPUB."""
    print(f"\n📚 Sommaire : {book.get_metadata('DC', 'title')[0][0]}")
    print("=" * 60)
    count = 0
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            print(f"[{count}] {item.get_name()}")
            count += 1
    print("=" * 60)

def read_chapter(book, chapter_index, width=80):
    """Lit et affiche le contenu d'un chapitre spécifique."""
    items = [i for i in book.get_items() if i.get_type() == ebooklib.ITEM_DOCUMENT]
    
    if chapter_index < 0 or chapter_index >= len(items):
        print(f"❌ Erreur : Index {chapter_index} invalide.")
        return

    item = items[chapter_index]
    print(f"\n📖 Lecture : {item.get_name()}")
    print("-" * width)
    
    soup = BeautifulSoup(item.get_content(), 'html.parser')
    text = soup.get_text()
    
    # Nettoyage basique pour l'affichage
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped:
            print(textwrap.fill(stripped, width=width))
            print() # Saut de ligne entre paragraphes
            
    print("-" * width)
    print("FIN DU CHAPITRE")

def export_txt(book, output_path):
    """Exporte tout le contenu de l'EPUB dans un seul fichier texte."""
    print(f"\n💾 Export vers {output_path}...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            title = book.get_metadata('DC', 'title')[0][0]
            f.write(f"{title}\n")
            f.write("=" * len(title) + "\n\n")
            
            count = 0
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    
                    header = f"--- Chapitre {count} : {item.get_name()} ---"
                    f.write(f"\n{header}\n")
                    f.write("-" * len(header) + "\n")
                    
                    lines = text.splitlines()
                    for line in lines:
                        stripped = line.strip()
                        if stripped:
                            f.write(textwrap.fill(stripped, width=80) + "\n\n")
                    count += 1
        print(f"✅ Export terminé : {count} chapitres exportés.")
    except Exception as e:
        print(f"❌ Erreur export : {e}")

def main():
    parser = argparse.ArgumentParser(description="Lecteur EPUB CLI")
    parser.add_argument("epub_path", help="Chemin vers le fichier EPUB")
    parser.add_argument("--list", "-l", action="store_true", help="Lister les chapitres")
    parser.add_argument("--read", "-r", type=int, help="Lire le chapitre (index)")
    parser.add_argument("--export", "-e", help="Exporter tout en .txt (chemin de sortie)")
    
    args = parser.parse_args()
    
    try:
        book = epub.read_epub(args.epub_path)
    except Exception as e:
        print(f"❌ Impossible de lire l'EPUB : {e}")
        sys.exit(1)

    if args.export:
        export_txt(book, args.export)
    elif args.list:
        list_chapters(book)
    elif args.read is not None:
        read_chapter(book, args.read)
    else:
        # Par défaut, on liste
        list_chapters(book)
        print("\n💡 Astuce : Utilisez --read <index> pour lire ou --export <file.txt> pour convertir.")

if __name__ == "__main__":
    main()
