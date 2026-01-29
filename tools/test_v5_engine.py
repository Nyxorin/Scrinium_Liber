import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dictionary import FrenchDictionary

print("--- Test du Moteur V5 (Pyspellchecker) ---")

try:
    dico = FrenchDictionary()
    stats = dico.stats()
    print(f"Stats: {stats}")
    
    test_words = [
        "maison",      # Simple
        "mangeaient",  # Conjugué (vieux Megalex avait du mal parfois)
        "anticonstitutionnellement", # Long
        "bonjoure",    # Faux
        "4ab",         # Faux OCR
        "l'arbre"      # Contraction
    ]
    
    for w in test_words:
        valid = dico.validate(w)
        print(f"'{w}': {'✅' if valid else '❌'}")
        
    # Test similar
    print(f"\nSuggestions pour 'bonjoure': {dico.get_similar('bonjoure')}")
    
except Exception as e:
    print(f"ERREUR V5: {e}")
