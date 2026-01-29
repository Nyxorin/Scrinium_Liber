import sys
import os
import json

# Ajout du root au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import get_composite_key
from core.knowledge_manager import KnowledgeManager
from correctors.semantic_corrector import SemanticCorrector

def test_memory():
    print("🧪 Test de la Phase 12 : La Mémoire")
    
    # 1. Test du Hachage de Contexte
    test_word = "trepignerent"
    test_context = "ils trepignerent de joie"
    key = get_composite_key(test_word, test_context)
    print(f"✓ Clé composite générée: {key}")
    assert "trepignerent|ils+___+de+joie" in key
    
    # 2. Test du KnowledgeManager
    kb_path = "data/knowledge/test_kb.jsonl"
    if os.path.exists(kb_path): os.remove(kb_path)
    
    km = KnowledgeManager(kb_path=kb_path)
    test_entry = {
        "key": key,
        "mot_source": "trepignerent",
        "mot_cible": "trépignèrent",
        "contexte_brut": test_context,
        "confidence": 1.0
    }
    km.add_correction(test_entry)
    
    # Reload and lookup
    km2 = KnowledgeManager(kb_path=kb_path)
    hit = km2.lookup(test_word, test_context)
    print(f"✓ Lookup Cache: {'Trouvé' if hit else 'Échec'}")
    assert hit['mot_cible'] == "trépignèrent"
    
    # 3. Test de Logging Session dans SemanticCorrector
    sc = SemanticCorrector(model_path="fake_model")
    sc.log_path = "data/knowledge/test_session.jsonl"
    if os.path.exists(sc.log_path): os.remove(sc.log_path)
    
    sc._log_validated_correction(test_context, "ils trépignèrent de joie")
    
    assert len(sc.session_log) > 0
    print(f"✓ Correction de session logguée: {sc.session_log[0]['mot_cible']}")
    
    print("\n✅ Tous les tests de la Phase 12 ont réussi !")

if __name__ == "__main__":
    test_memory()
