"""
Module CORRECTORS - Modules de correction (Odoo principle)

Chaque correcteur hérite de BaseCorrector et implémente:
- correct(): Applique les corrections
- get_confidence(): Niveau de confiance
- get_name(): Nom du correcteur

Pipeline de correction (ordre):
1. DeterministicCorrector - Règles fixes (confiance: 100%)
2. DictionaryValidator - Validation Megalex (confiance: 100%)
3. TransformerSuggester - Suggestions IA (confiance: 90%)
4. GrammarValidator - Analyse grammaticale (confiance: 90%)
5. LLMCorrector - Cas complexes (confiance: 80%)
6. HumanValidator - Validation finale (confiance: 100%)
"""

from .base_corrector import BaseCorrector, CorrectionSuggestion, CorrectionPipeline
from .deterministic_corrector import DeterministicCorrector
from .dictionary_validator import DictionaryValidator

__all__ = [
    'BaseCorrector',
    'CorrectionSuggestion',
    'CorrectionPipeline',
    'DeterministicCorrector',
    'DictionaryValidator',
]
