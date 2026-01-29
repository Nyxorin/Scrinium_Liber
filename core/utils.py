import re
import hashlib

def extraire_fenetre(contexte, mot_cible, n=2):
    """
    Extrait les n mots avant et après le mot cible dans le contexte.
    """
    # Nettoyage basique pour la tokenisation
    tokens = re.findall(r"\w+", contexte.lower())
    mot_cible_lower = mot_cible.lower()
    
    try:
        idx = tokens.index(mot_cible_lower)
        start = max(0, idx - n)
        end = min(len(tokens), idx + n + 1)
        
        window = tokens[start:end]
        # On remplace le mot cible par un placeholder pour le pattern
        window[idx - start] = "___"
        return window
    except ValueError:
        # Si le mot n'est pas trouvé tel quel (ex: ponctuation collée)
        return ["UNKNOWN_CONTEXT"]

def hash_pattern(words):
    """
    Crée une chaîne de caractères stable représentant le pattern.
    """
    return "+".join(words)

def get_composite_key(mot_errone, contexte):
    """
    Génère la clé composite mot|pattern.
    """
    window = extraire_fenetre(contexte, mot_errone)
    pattern = hash_pattern(window)
    return f"{mot_errone.lower()}|{pattern}"
