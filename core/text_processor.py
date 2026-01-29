#!/usr/bin/env python3
"""
Module de traitement de texte - Extraction et normalisation.
Module CORE - Base commune solide (Odoo principle)
"""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub


class TextProcessor:
    """
    Processeur de texte universel.
    Principe Odoo: Base commune solide, extensible par héritage.
    """

    def __init__(self):
        pass

    @staticmethod
    def extract_from_epub(epub_path: str) -> str:
        """
        Extrait tout le texte d'un fichier EPUB.

        Args:
            epub_path: Chemin du fichier EPUB

        Returns:
            Texte complet du livre
        """
        book = epub.read_epub(epub_path)
        texts = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text()
                    texts.append(text)
                except Exception as e:
                    print(f"⚠️ Erreur extraction chapitre: {e}")
                    continue

        return '\n'.join(texts)

    @staticmethod
    def extract_from_html(html_content: str) -> str:
        """
        Extrait le texte d'un contenu HTML.

        Args:
            html_content: Contenu HTML

        Returns:
            Texte extrait
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalise les espaces blancs.

        Args:
            text: Texte à normaliser

        Returns:
            Texte normalisé
        """
        # Espaces multiples → simple
        text = re.sub(r' {2,}', ' ', text)

        # Sauts de ligne multiples → double
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Espaces en début/fin de ligne
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text

    @staticmethod
    def split_into_paragraphs(text: str) -> List[str]:
        """
        Découpe le texte en paragraphes.

        Args:
            text: Texte à découper

        Returns:
            Liste de paragraphes
        """
        # Séparer par doubles sauts de ligne
        paragraphs = text.split('\n\n')

        # Filtrer les paragraphes vides
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        Découpe le texte en phrases.

        Args:
            text: Texte à découper

        Returns:
            Liste de phrases
        """
        # Pattern pour détecter les fins de phrase
        # Prend en compte: . ! ? suivi d'espace et majuscule
        pattern = r'(?<=[.!?])\s+(?=[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ])'

        sentences = re.split(pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    @staticmethod
    def split_into_words(text: str) -> List[str]:
        """
        Découpe le texte en mots.

        Args:
            text: Texte à découper

        Returns:
            Liste de mots
        """
        # Pattern pour extraire les mots (lettres, chiffres, apostrophes, traits d'union)
        pattern = r"\b[\w'àâäéèêëïîôöùûüÿç-]+\b"
        words = re.findall(pattern, text, re.UNICODE)

        return words

    @staticmethod
    def find_suspect_words(text: str) -> List[Tuple[str, int]]:
        """
        Trouve les mots contenant des caractères suspects (probables erreurs OCR).

        Args:
            text: Texte à analyser

        Returns:
            Liste de tuples (mot_suspect, position)
        """
        suspect_words = []

        # Pattern: caractères qui ne devraient jamais être dans un mot français
        pattern = r'\b\w*[0-9@*%&#$^`\[\]|]+\w*\b'

        for match in re.finditer(pattern, text):
            word = match.group()
            # Ignorer les vrais nombres
            if not word.isdigit():
                suspect_words.append((word, match.start()))

        return suspect_words

    @staticmethod
    def rebuild_html(text: str, original_html: str) -> str:
        """
        Reconstruit le HTML avec le texte corrigé.

        Args:
            text: Texte corrigé
            original_html: HTML original (pour récupérer le head)

        Returns:
            HTML reconstruit
        """
        # Extraire le <head> de l'original
        soup = BeautifulSoup(original_html, 'html.parser')
        head = soup.find('head')
        head_html = str(head) if head else '<head><meta charset="UTF-8"/></head>'

        # Découper en paragraphes
        paragraphs = TextProcessor.split_into_paragraphs(text)

        # Créer le body avec des <p>
        body_content = '\n'.join(f'<p class="calibre1">{p}</p>' for p in paragraphs)

        # Construire le HTML complet
        new_html = f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
{head_html}
<body>
{body_content}
</body>
</html>"""

        return new_html

    @staticmethod
    def count_words(text: str) -> int:
        """Compte le nombre de mots"""
        return len(TextProcessor.split_into_words(text))

    @staticmethod
    def count_characters(text: str) -> int:
        """Compte le nombre de caractères"""
        return len(text)

    @staticmethod
    def get_stats(text: str) -> dict:
        """
        Retourne les statistiques du texte.

        Args:
            text: Texte à analyser

        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            'characters': TextProcessor.count_characters(text),
            'words': TextProcessor.count_words(text),
            'paragraphs': len(TextProcessor.split_into_paragraphs(text)),
            'sentences': len(TextProcessor.split_into_sentences(text)),
            'suspect_words': len(TextProcessor.find_suspect_words(text))
        }

    @staticmethod
    def print_stats(text: str):
        """Affiche les statistiques du texte"""
        stats = TextProcessor.get_stats(text)

        print("=" * 80)
        print("📊 STATISTIQUES DU TEXTE (Module CORE)")
        print("=" * 80)
        print(f"✓ Caractères: {stats['characters']:,}")
        print(f"✓ Mots: {stats['words']:,}")
        print(f"✓ Paragraphes: {stats['paragraphs']:,}")
        print(f"✓ Phrases: {stats['sentences']:,}")
        print(f"⚠️ Mots suspects: {stats['suspect_words']:,}")
        print("=" * 80)


if __name__ == "__main__":
    # Test avec un texte simple
    test_text = """Voici un texte d'exemple.

    Il contient plusieurs paragraphes. Et plusieurs phrases !

    Ainsi que des mots suspects: d7un, l@homme, mil icien."""

    print("🧪 Test du TextProcessor:")
    print()
    TextProcessor.print_stats(test_text)

    print("\n🔍 Mots suspects détectés:")
    suspects = TextProcessor.find_suspect_words(test_text)
    for word, pos in suspects:
        print(f"   '{word}' à position {pos}")
