#!/usr/bin/env python3
"""
Base de données complète des erreurs OCR standards.
Module CORE - Base commune solide (Odoo principle)

Compilée depuis:
- PGDP Wiki (Project Gutenberg)
- Recherches académiques (ICDAR, OCR-D)
- Patterns observés dans livres français
"""

# ============================================================================
# CONFUSIONS DE CARACTÈRES STANDARDS
# ============================================================================

CHARACTER_CONFUSIONS = {
    # Chiffres ↔ Lettres (très fréquent)
    '0': ['o', 'O', 'ô', 'ö'],
    '1': ['l', 'i', 'I', '|'],
    '2': ['z', 'Z'],
    '3': ['e', 'E', 'B'],
    '4': ['a', 'A', 'q'],
    '5': ['s', 'S'],
    '6': ['b', 'G', 'g'],
    '7': ["'", 't', 'T'],  # TRÈS fréquent en français !
    '8': ['b', 'B'],
    '9': ['g', 'q'],

    # Lettres confondues (minuscules)
    'l': ['1', 'i', '|', 't'],
    'i': ['1', 'l', '!', '|'],
    'o': ['0', 'c', 'e'],
    'c': ['e', 'o'],
    'e': ['c', 'o'],
    'n': ['ri', 'rn', 'u'],  # "Banks" → "Bariks"
    'm': ['rn', 'ni'],
    'u': ['n', 'v'],
    'v': ['u', 'y'],
    'w': ['vv', 'uu'],

    # Lettres confondues (majuscules)
    'I': ['l', '1', '|'],
    'O': ['0', 'Q', 'D'],
    'D': ['O', 'Q'],
    'Q': ['O', 'D'],
    'B': ['8', 'R'],
    'S': ['5', '8'],

    # Caractères spéciaux → Apostrophes/Guillemets
    '@': ["'"],
    '*': ["'"],
    '`': ["'"],
    '^': ["'"],
    '~': ['-'],
    '_': ['-'],
    '|': ['l', 'i', 'I'],
    ']': ['l'],
    '[': ['l'],
    '}': [')'],
    '{': ['('],

    # Symboles → Lettres
    '%': ['', 's'],
    '&': [''],
    '#': [''],
    '$': ['s', 'S'],
    '§': ['s'],
    '¢': ['c'],
    '£': ['E'],

    # Ponctuation confondue
    '!': ['l', 'i', '1'],
    ',': ['.', ';'],
    ';': [':', ','],
    ':': [';'],
}

# ============================================================================
# ERREURS SPÉCIFIQUES AU FRANÇAIS
# ============================================================================

FRENCH_SPECIFIC_ERRORS = {
    # Accents mal reconnus
    'à': ['a', 'A', ''],  # Supprimé ou mal lu
    'â': ['a', 'a', 'A'],
    'é': ['e', 'e', 'E', 'ê'],
    'è': ['e', 'e', 'E'],
    'ê': ['e', 'e', 'E', 'ë'],
    'ë': ['e', 'e', 'E'],
    'î': ['i', 'i', 'I'],
    'ï': ['i', 'i', 'I', 'ij'],
    'ô': ['o', 'o', 'O', '0'],
    'ù': ['u', 'u', 'U'],
    'û': ['u', 'u', 'U'],
    'ü': ['u', 'u', 'U'],
    'ç': ['c', 'c', 'C', 'ĉ'],

    # Ligatures
    'œ': ['oe', 'ce'],
    'Œ': ['OE', 'CE'],
    'æ': ['ae'],
    'Æ': ['AE'],
    'ﬁ': ['fi'],
    'ﬂ': ['fl'],
    'ﬀ': ['ff'],
    'ﬃ': ['ffi'],
    'ﬄ': ['ffl'],

    # Guillemets français
    '«': ['"', "''", '<<'],
    '»': ['"', "''", '>>'],
    '"': ['«', '»', "''"],
    '"': ['«', '»', "''"],
    ''': ["'", '`'],
    ''': ["'", '`'],
}

# ============================================================================
# PATTERNS DE MOTS (Fréquents)
# ============================================================================

COMMON_WORD_PATTERNS = {
    # Contractions avec apostrophe mal lue
    r"\bd['`@*7]": "d'",      # d7un → d'un
    r"\bn['`@*7]": "n'",      # n7avait → n'avait
    r"\bl['`@*7]": "l'",      # l@homme → l'homme
    r"\bqu['`@*7]": "qu'",    # qu7il → qu'il
    r"\bc['`@*7]": "c'",      # c7est → c'est
    r"\bj['`@*7]": "j'",      # j7ai → j'ai
    r"\bm['`@*7]": "m'",      # m7a → m'a
    r"\bs['`@*7]": "s'",      # s7en → s'en
    r"\bt['`@*7]": "t'",      # t7as → t'as

    # "rn" / "ni" / "m" confusion
    r"\brn\b": "m",           # "rn" isolé → "m"
    r"\bni\b": "m",           # "ni" isolé → "m"

    # Espaces parasites dans mots courants
    r"\be n\b": "en",
    r"\bd e\b": "de",
    r"\bl e\b": "le",
    r"\bl a\b": "la",
    r"\bq u\b": "qu",
    r"\bp o\b": "po",

    # Lettres doublées par erreur
    r"\b([lLtTmMnNrR])\1{3,}\b": r"\1\1",  # llll → ll
}

# ============================================================================
# ERREURS DE MISE EN PAGE
# ============================================================================

LAYOUT_ERRORS = {
    # Manque espaces après ponctuation
    r"([.!?,:;])([A-Z])": r"\1 \2",

    # Espaces avant ponctuation (français)
    r"\s+([!?:;»])": r"\1",  # Garder colle
    r"([«])\s+": r"\1",      # Garder colle

    # Tirets multiples
    r"--+": "—",  # -- → em-dash

    # Césures en fin de ligne
    r"(\w+)-\s*\n\s*(\w+)": r"\1\2",

    # Sauts de ligne multiples
    r"\n{3,}": "\n\n",

    # Espaces multiples
    r" {2,}": " ",
}

# ============================================================================
# PATTERNS CONTEXTUELS (Règles grammaticales)
# ============================================================================

CONTEXTUAL_PATTERNS = {
    # Mots qui ne peuvent pas suivre certains
    "invalids_after_article": {
        "le": ["le", "la", "les", "un", "une", "des"],  # Pas 2 articles
        "la": ["le", "la", "les", "un", "une", "des"],
        "les": ["le", "la", "les", "un", "une", "des"],
    },

    # Terminaisons verbales impossibles
    "impossible_endings": [
        "ait7",  # Devrait être "ait"
        "aient7",
        "er7",
    ],
}

# ============================================================================
# CONTRACTIONS FRANÇAISES VALIDES (Protection)
# ============================================================================

VALID_FRENCH_CONTRACTIONS = {
    'n', 'l', 'd', 'c', 'j', 'm', 't', 's', 'qu'
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_all_character_substitutions():
    """Retourne toutes les substitutions possibles (chars + français)"""
    all_subs = {}
    all_subs.update(CHARACTER_CONFUSIONS)
    all_subs.update(FRENCH_SPECIFIC_ERRORS)
    return all_subs


def generate_correction_candidates(word, max_candidates=5):
    """
    Génère des candidats de correction pour un mot erroné.
    Utilise la base de données de confusions.
    """
    candidates = set()
    subs = get_all_character_substitutions()

    # Pour chaque caractère du mot
    for i, char in enumerate(word):
        if char in subs:
            # Essayer chaque remplacement possible
            for replacement in subs[char]:
                candidate = word[:i] + replacement + word[i+1:]
                if candidate != word:  # Pas l'original
                    candidates.add(candidate)

                # Limiter le nombre
                if len(candidates) >= max_candidates * 2:
                    break

    return list(candidates)[:max_candidates]


def get_confusion_score(char1, char2):
    """
    Retourne un score de similarité entre 2 caractères.
    Basé sur les confusions OCR connues.
    """
    subs = get_all_character_substitutions()

    if char1 == char2:
        return 1.0

    # Vérifier si c'est une confusion connue
    if char1 in subs and char2 in subs[char1]:
        return 0.8  # Haute probabilité de confusion

    if char2 in subs and char1 in subs[char2]:
        return 0.8

    # Similitude visuelle basique
    similar_pairs = [
        ('o', '0'), ('l', '1'), ('l', 'i'), ('I', '1'),
        ('O', '0'), ('S', '5'), ('B', '8'),
    ]

    for a, b in similar_pairs:
        if (char1 == a and char2 == b) or (char1 == b and char2 == a):
            return 0.6

    return 0.0  # Pas de similarité


# ============================================================================
# STATISTIQUES
# ============================================================================

def print_database_stats():
    """Affiche les statistiques de la base de données"""
    print("=" * 80)
    print("📊 BASE DE DONNÉES D'ERREURS OCR (Module CORE)")
    print("=" * 80)
    print()

    char_subs = CHARACTER_CONFUSIONS
    french_subs = FRENCH_SPECIFIC_ERRORS
    patterns = COMMON_WORD_PATTERNS

    print(f"✓ Confusions de caractères standard : {len(char_subs)}")
    print(f"✓ Erreurs spécifiques français : {len(french_subs)}")
    print(f"✓ Patterns de mots courants : {len(patterns)}")
    print(f"✓ Erreurs de mise en page : {len(LAYOUT_ERRORS)}")
    print()

    total_substitutions = sum(len(v) for v in char_subs.values())
    total_substitutions += sum(len(v) for v in french_subs.values())

    print(f"📈 Total de substitutions possibles : {total_substitutions}")
    print("=" * 80)


if __name__ == "__main__":
    print_database_stats()

    # Test
    print("\n🧪 Test de génération de candidats:")
    test_word = "d7un"
    candidates = generate_correction_candidates(test_word)
    print(f"   Mot: '{test_word}'")
    print(f"   Candidats: {candidates}")
