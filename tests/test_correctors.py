import pytest
import re
from correctors.deterministic_corrector import DeterministicCorrector

@pytest.fixture
def corrector():
    return DeterministicCorrector()

def test_simple_replacements(corrector):
    assert corrector.correct("d7un homme") == "d'un homme"
    assert corrector.correct("l@Afrique") == "l'Afrique"
    # mi] icien -> mil icien (simple) -> milicien (regex)
    assert corrector.correct("mi] icien") == "milicien"

def test_ocr_number_confusion(corrector):
    # m0ment -> moment
    assert corrector.correct("m0ment") == "moment"
    assert corrector.correct("C7était") == "C'était"
    assert corrector.correct("1es maisons") == "les maisons"
    assert corrector.correct("M15SION") == "MISSION"

def test_layout_fixes(corrector):
    assert corrector.correct("Le texte.Sans espace") == "Le texte. Sans espace"
    assert corrector.correct("Beaucoup     d'espaces") == "Beaucoup d'espaces"
    assert corrector.correct("Ligne 1-\nLigne 2") == "Ligne 1Ligne 2"

def test_title_removal(corrector):
    # MISSION IMPOSSIBLE EN SOMALIE -> empty
    # "Texte MISSION IMPOSSIBLE EN SOMALIE 123 Fin" -> "Texte  Fin" -> "Texte Fin" (multiple spaces fix)
    assert corrector.correct("Texte MISSION IMPOSSIBLE EN SOMALIE 123 Fin") == "Texte Fin"

def test_weird_characters(corrector):
    assert corrector.correct("oŸ") == "où"
    assert corrector.correct("Ÿn") == "Mn"
    assert corrector.correct("chaufŒ") == "chauff"
    assert corrector.correct("Œ isolé") == "M isolé"
