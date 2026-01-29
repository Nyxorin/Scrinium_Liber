"""
Module CORE - Base commune solide (Odoo principle)

Ce module contient les composants de base réutilisables:
- dictionary.py: Gestionnaire du dictionnaire français enrichi
- ocr_patterns.py: Base de données des erreurs OCR
- text_processor.py: Extraction et normalisation de texte
"""

from .dictionary import FrenchDictionary
from .ocr_patterns import (
    CHARACTER_CONFUSIONS,
    FRENCH_SPECIFIC_ERRORS,
    COMMON_WORD_PATTERNS,
    LAYOUT_ERRORS,
    VALID_FRENCH_CONTRACTIONS,
    get_all_character_substitutions,
    generate_correction_candidates,
    get_confusion_score,
)
from .text_processor import TextProcessor

__all__ = [
    'FrenchDictionary',
    'TextProcessor',
    'CHARACTER_CONFUSIONS',
    'FRENCH_SPECIFIC_ERRORS',
    'COMMON_WORD_PATTERNS',
    'LAYOUT_ERRORS',
    'VALID_FRENCH_CONTRACTIONS',
    'get_all_character_substitutions',
    'generate_correction_candidates',
    'get_confusion_score',
]
