#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from drq_gym.defender import Defender

def main():
    # Configuration
    input_file = os.path.join(project_root, "livres_traites", "SAS_047_Mission_Impossible.txt")
    
    # Generate timestamp for versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_name = f"SAS_047_Mission_Impossible_en_Somalie_v{timestamp}.txt"
    output_file = os.path.join(project_root, "livres_corriges", version_name)
    
    model_path = os.path.join(project_root, "models", "mistral-7b-instruct-v0.3.Q4_K_M.gguf")
    blacklist_path = os.path.join(project_root, "drq_gym", "blacklist.json")
    
    print(f"--- Démarrage de la correction de SAS 047 ---")
    print(f"Entrée : {input_file}")
    print(f"Sortie : {output_file}")
    print(f"Modèle : {model_path}")

    if not os.path.exists(input_file):
        print(f"❌ Erreur : Fichier d'entrée introuvable.")
        return

    # Initialize Defender
    print("🛡️ Initialisation du Defender...")
    try:
        defender = Defender(model_path, "chroma_db_path_placeholder", blacklist_path)
    except Exception as e:
        print(f"❌ Erreur d'initialisation du Defender: {e}")
        return

    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"📄 {total_lines} lignes à traiter.")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    start_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                f_out.write("\n")
                continue

            print(f"[{i+1}/{total_lines}] Correction...", end='\r')
            
            try:
                # Correction via Defender (Pipeline complet: Deterministic -> Immune -> Semantic)
                corrected_line = defender.clean(line)
                f_out.write(corrected_line + "\n")
                f_out.flush() # Ensure we save progress
            except Exception as e:
                print(f"\n❌ Erreur ligne {i+1}: {e}")
                f_out.write(line + "\n") # Fallback to original

    elapsed = time.time() - start_time
    print(f"\n✅ Correction terminée en {elapsed:.2f} secondes.")
    print(f"📁 Fichier sauvegardé : {output_file}")

if __name__ == "__main__":
    main()
