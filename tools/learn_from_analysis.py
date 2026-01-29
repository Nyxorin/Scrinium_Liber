import json
import sys
import os
from datetime import datetime

def populate_kb(analysis_json, kb_jsonl):
    print(f"Ingesting corrections from {analysis_json}...")
    
    if not os.path.exists(analysis_json):
        print(f"Error: {analysis_json} not found.")
        return

    with open(analysis_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    details = data.get('details', [])
    new_entries = 0
    
    # Open KB in append mode
    os.makedirs(os.path.dirname(kb_jsonl), exist_ok=True)
    
    with open(kb_jsonl, 'a', encoding='utf-8') as f_kb:
        for entry in details:
            if entry['type'] == 'replace':
                # We extract the most meaningful change
                # (Simple heuristic: if original and cleaned are single lines)
                orig = entry['original'].strip()
                clean = entry['cleaned'].strip()
                
                # Filter out very long segments (we want lexical/short contextual rules)
                if len(orig) < 100 and len(clean) < 100:
                    kb_entry = {
                        "original": orig,
                        "corrected": clean,
                        "source": "auto-v2",
                        "timestamp": datetime.now().isoformat()
                    }
                    f_kb.write(json.dumps(kb_entry, ensure_ascii=False) + "\n")
                    new_entries += 1
                    
    print(f"Success: {new_entries} entries added to {kb_jsonl}.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python learn_from_analysis.py <analysis.json> <knowledge.jsonl>")
    else:
        populate_kb(sys.argv[1], sys.argv[2])
