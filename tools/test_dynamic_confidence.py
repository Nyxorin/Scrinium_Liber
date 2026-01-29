import sys
import os
import json

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_manager import KnowledgeManager
from tools.consolidate_memory import consolidate

def test_confidence():
    print("🧪 Test de la Confiance Dynamique (V7)")
    
    kb_path = "data/knowledge/test_dynamic_kb.jsonl"
    sess_path = "data/knowledge/test_dynamic_sess.jsonl"
    
    if os.path.exists(kb_path): os.remove(kb_path)
    if os.path.exists(sess_path): os.remove(sess_path)
    
    # 1. Création d'une première session (1ère vue)
    entry = {
        "key": "poximité|par+la+___+de+l",
        "mot_source": "poximité",
        "mot_cible": "proximité",
        "contexte_brut": "adouci par la poximité de l'océan",
        "timestamp": "2026-01-19T10:00:00",
        "confidence": 1.0 # Toujours 1.0 dans le log car validé par agents
    }
    
    with open(sess_path, 'w') as f:
        f.write(json.dumps(entry) + "\n")
    
    print("\n1. Première consolidation (Vue n°1)")
    consolidate(sess_path, kb_path)
    
    km = KnowledgeManager(kb_path=kb_path)
    hit = km.lookup("poximité", "adouci par la poximité de l'océan")
    print(f"   Confiance: {hit['confidence']}, Count: {hit['count']}")
    print(f"   Can Fast-Track: {hit.get('can_fast_track')}")
    
    assert hit['confidence'] == 0.5
    assert hit['can_fast_track'] == False
    
    # 2. Deuxième consolidation (Même correction, Vue n°2)
    print("\n2. Deuxième consolidation (Vue n°2)")
    consolidate(sess_path, kb_path) # On réutilise le même log pour simuler
    
    km2 = KnowledgeManager(kb_path=kb_path)
    hit2 = km2.lookup("poximité", "adouci par la poximité de l'océan")
    print(f"   Confiance: {hit2['confidence']}, Count: {hit2['count']}")
    print(f"   Can Fast-Track: {hit2.get('can_fast_track')}")
    
    assert hit2['confidence'] == 1.0
    assert hit2['can_fast_track'] == True
    
    print("\n✅ Test de la Confiance Dynamique réussi !")

if __name__ == "__main__":
    test_confidence()
