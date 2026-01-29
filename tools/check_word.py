import sys
import os

# Add root to path to find core
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from core.dictionary import FrenchDictionary

try:
    dico = FrenchDictionary()
    word = "ubuesque"
    is_present = dico.validate(word)
    print(f"Mot '{word}' dans Megalex : {is_present}")
    
    if not is_present:
        print(f"Similar: {dico.get_similar(word)}")
except Exception as e:
    print(f"Error: {e}")
