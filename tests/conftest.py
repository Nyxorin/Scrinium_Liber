import sys
from pathlib import Path

# Ajouter le répertoire racine au sys.path pour les imports des modules
sys.path.insert(0, str(Path(__file__).parent.parent))
