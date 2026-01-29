import json
import os
from typing import Dict, Optional, List
from .utils import get_composite_key

class KnowledgeManager:
    """
    Gère la base de connaissances (master_kb.jsonl) et fournit des capacités
    de cache intelligent et de recherche RAG.
    """
    
    def __init__(self, kb_path: str = "data/knowledge/master_kb.jsonl"):
        self.kb_path = kb_path
        self.memory: Dict[str, dict] = {} # Key: composite_key, Value: entry
        self.load_memory()

    def load_memory(self):
        """Charge la mémoire depuis le fichier JSONL."""
        if not os.path.exists(self.kb_path):
            return
            
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        key = entry.get('key')
                        if key:
                            # On initialise count à 1 si absent (compatibilité V6)
                            if 'count' not in entry:
                                entry['count'] = 1
                            # On initialise confidence si absent
                            if 'confidence' not in entry:
                                entry['confidence'] = 1.0
                            self.memory[key] = entry
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de la mémoire: {e}")

    def lookup(self, word: str, context: str) -> Optional[dict]:
        """
        Cherche une correction connue pour un mot dans son contexte.
        Retourne l'entrée si trouvée, avec un flag 'can_fast_track'.
        """
        key = get_composite_key(word, context)
        entry = self.memory.get(key)
        if entry:
            # Seuil de confiance pour le Fast-Track (bypass LLM)
            # Un mot vu 2+ fois ou avec une confiance explicite de 1.0 est fast-trackable.
            entry['can_fast_track'] = entry.get('confidence', 0) >= 0.9 or entry.get('count', 1) >= 2
        return entry

    def get_precedents(self, text: str, k: int = 3) -> List[dict]:
        """
        Recherche RAG (simple) pour trouver des exemples proches lexicalement.
        """
        # Pour l'instant, simple match sur les mots sources présents dans le texte
        matches = []
        text_lower = text.lower()
        for entry in self.memory.values():
            if entry['mot_source'].lower() in text_lower:
                matches.append(entry)
                if len(matches) >= k:
                    break
        return matches

    def add_correction(self, entry: dict):
        """Ajoute une nouvelle correction validée à la mémoire."""
        key = entry.get('key')
        if not key:
            return
            
        # Mise à jour mémoire vive
        self.memory[key] = entry
        
        # Sauvegarde persistante (append)
        os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
        with open(self.kb_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
