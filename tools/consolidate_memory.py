import json
import os
import sys

def consolidate(session_path, master_path):
    if not os.path.exists(session_path):
        print(f"No session log found at {session_path}")
        return

    print(f"Consolidating {session_path} into {master_path}...")
    
    # Load master to memory
    master_data = {}
    if os.path.exists(master_path):
        with open(master_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    master_data[entry['key']] = entry

    new_entries = 0
    updated_entries = 0
    
    if os.path.exists(session_path):
        with open(session_path, 'r', encoding='utf-8') as f_sess:
            for line in f_sess:
                if line.strip():
                    entry = json.loads(line)
                    key = entry['key']
                    
                    if key in master_data:
                        # On incrémente le compteur
                        master_data[key].setdefault('count', 1)
                        master_data[key]['count'] += 1
                        # Si vu 2 fois, la confiance passe à 1.0 (Fast-Trackable)
                        if master_data[key]['count'] >= 2:
                            master_data[key]['confidence'] = 1.0
                        updated_entries += 1
                    else:
                        # Nouvelle entrée : confiance initiale 0.5 (Nécessite 2 vues pour Fast-Track)
                        entry['count'] = 1
                        entry['confidence'] = 0.5
                        master_data[key] = entry
                        new_entries += 1

    # Réécriture complète de la Master KB (plus propre pour les mises à jour)
    with open(master_path, 'w', encoding='utf-8') as f_mast:
        for entry in master_data.values():
            f_mast.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Success: {new_entries} new, {updated_entries} updated corrections in Master KB.")
    # Optional: Clear session log after consolidation
    # os.remove(session_path)

if __name__ == "__main__":
    session = "data/knowledge/session_corrections.jsonl"
    master = "data/knowledge/master_kb.jsonl"
    consolidate(session, master)
