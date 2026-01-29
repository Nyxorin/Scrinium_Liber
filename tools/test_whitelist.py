import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.dictionary import FrenchDictionary

def test_whitelist():
    print("🧪 Test du Système de Whitelist (V7)")
    
    # Création du dico
    d = FrenchDictionary()
    
    # Cas 1: Mot français standard
    assert d.validate("maison") == True
    print("✓ Mot standard 'maison' OK")
    
    # Cas 2: Mot inconnu (pas dans dico, pas dans whitelist)
    assert d.validate("latigouste") == False
    print("✓ Mot inconnu 'latigouste' rejeté (Correct)")
    
    # Cas 3: Mot dans Whitelist (Malko)
    assert d.validate("Malko") == True
    print("✓ Mot 'Malko' (Whitelist) accepté !")
    
    # Cas 4: Mot dans Whitelist avec apostrophe (l'Malko)
    assert d.validate("l'Malko") == True
    print("✓ Mot 'l'Malko' (Whitelist) accepté !")

    print("\n✅ Test de la Whitelist réussi !")

if __name__ == "__main__":
    test_whitelist()
