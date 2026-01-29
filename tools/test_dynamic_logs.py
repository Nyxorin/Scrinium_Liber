import sys
import os
from datetime import datetime

# Root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from epub_cleaner_complete import CompleteEPUBCleaner

def test_dynamic_logging():
    print("🧪 Test de la Phase 12 : Organisation des Logs")
    
    input_file = "livres_corriges/SAS_047_SMART_CLEAN_V2.epub"
    if not os.path.exists(input_file):
        print(f"❌ Fichier source {input_file} manquant.")
        return

    cleaner = CompleteEPUBCleaner(input_file)
    
    print("\n1. Chargement de l'EPUB (devrait initialiser le log)...")
    if cleaner.load_epub():
        log_path = cleaner.semantic.log_path
        print(f"✓ Log path généré : {log_path}")
        
        # Vérification du format : session_TITRE_DATE_HEURE.jsonl
        if "session_" in log_path and ".jsonl" in log_path:
            print("✓ Format du nom de fichier OK")
        else:
            print("❌ Format du nom de fichier incorrect")
            
        # Vérification de l'existence du dossier
        if os.path.exists(os.path.dirname(log_path)):
            print("✓ Dossier de logs OK")
        else:
            print("❌ Dossier de logs manquant")

    print("\n✅ Test terminé.")

if __name__ == "__main__":
    test_dynamic_logging()
