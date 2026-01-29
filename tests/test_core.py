import pytest
import os
from core.text_processor import TextProcessor
from core.dictionary import FrenchDictionary

def test_text_processor_stats():
    text = "C'est un test. Avec sept mots et suspect d7un."
    stats = TextProcessor.get_stats(text)
    assert stats['words'] > 0
    assert stats['suspect_words'] >= 1

def test_text_processor_normalize():
    text = "Beaucoup     d'espaces.  \n\n\nPlusieurs lignes."
    normalized = TextProcessor.normalize_whitespace(text)
    assert "  " not in normalized
    assert "\n\n\n" not in normalized

def test_dictionary_basic():
    # Note: this might fail if megalex is not present in the tests dir, 
    # but the class should handle it gracefully.
    d = FrenchDictionary()
    assert d.validate("maison") or not os.path.exists("dictionnaire_francais.pkl")
    assert d.validate("d'un")
