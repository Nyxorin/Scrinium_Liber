import sys
import os
import json

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from correctors.semantic_corrector import SemanticCorrector

def test_surgical_learning():
    print("🧪 Test de l'Apprentissage Chirurgical (Diff-based)")
    
    sc = SemanticCorrector(model_path="fake_model")
    sc.log_path = "data/knowledge/test_surgical.jsonl"
    if os.path.exists(sc.log_path): 
        os.remove(sc.log_path)
    
    # Cas 1: Suppression de tiret (Le bruit identifié dans l'audit)
    original_1 = "- Dépêchons-nous !"
    corrected_1 = "Dépêchons-nous !"
    
    print("\n1. Test suppression de tiret (devrait loguer 0 entrée)")
    sc._log_validated_correction(original_1, corrected_1)
    
    log_count = 0
    if os.path.exists(sc.log_path):
        with open(sc.log_path, 'r') as f:
            log_count = len(f.readlines())
    
    print(f"   Log count: {log_count}")
    assert log_count == 0, f"Erreur: {log_count} entrées logguées pour une suppression de tiret"
    
    # Cas 2: Substitution réelle au milieu d'une phrase
    original_2 = "La poximité de l'océan est agréable."
    corrected_2 = "La proximité de l'océan est agréable."
    
    print("\n2. Test substitution réelle (devrait loguer 1 entrée)")
    sc._log_validated_correction(original_2, corrected_2)
    
    with open(sc.log_path, 'r') as f:
        entries = [json.loads(line) for line in f]
    
    print(f"   Entries logguées: {len(entries)}")
    assert len(entries) == 1
    assert entries[0]['mot_source'] == "poximité"
    assert entries[0]['mot_cible'] == "proximité"
    
    print("\n✅ Test de l'Apprentissage Chirurgical réussi !")

if __name__ == "__main__":
    test_surgical_learning()
