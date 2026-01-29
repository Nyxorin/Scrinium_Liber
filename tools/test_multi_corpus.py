
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.saboteur import Saboteur

if __name__ == "__main__":
    sab = Saboteur()
    # The load_corpus method should now find 3 files: SAS_006, SAS_005, SAS_011
    sab.load_corpus()
    print(f"✅ Saboteur initialized with {len(sab.corpus_lines)} lines.")
    
    # Check if lines are actually from different books (optional debug)
    # Since we can't easily check book source from lines alone without more metadata,
    # just confirming the total line count is sufficient.
