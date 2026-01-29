import logging
import subprocess
import json
import os
import sys
from typing import Dict, List, Optional

# Plus d'import de transformers ici !
# Plus de config d'environnement non plus, c'est géré par le daemon.

from correctors.semantic_corrector import SemanticCorrector

class NERAgent:
    """
    Agent 'ProperNounDetector' (Phase 17).
    Architecture Daemon :
    - Lance 'core/ner_daemon.py' en sous-processus isolé.
    - Communique via stdin/stdout (JSON).
    - Permet la cohabitation PyTorch (Daemon) et Llama.cpp (Principal).
    """
    
    def __init__(self, use_flaubert: bool = True):
        self.logger = logging.getLogger("NERAgent")
        self.use_flaubert = use_flaubert
        self.daemon_process = None
        
        # 1. Lancer le Daemon si requis
        if self.use_flaubert:
            self._start_daemon()
            
        # 2. Charger Mistral (Llama.cpp) dans ce processus principal
        # (Aucun conflit possible car Torch n'est pas chargé ici)
        self.semantic = SemanticCorrector()

    def _start_daemon(self):
        """Lance le processus satellite CamemBERT."""
        daemon_path = os.path.join(os.path.dirname(__file__), "ner_daemon.py")
        
        # [CRITICAL] On utilise l'environnement virtuel dédié (.ner_env) 
        # pour garantir l'isolation des dépendances (Torch vs System libs)
        venv_python = os.path.join(os.getcwd(), ".ner_env", "bin", "python3")
        
        if not os.path.exists(venv_python):
            self.logger.warning(f"⚠️ Venv NER introuvable ({venv_python}). Fallback sur sys.executable (Risque de crash).")
            venv_python = sys.executable

        try:
            print(f"🚀 Démarrage du Daemon NER ({daemon_path}) avec {venv_python}...")
            self.daemon_process = subprocess.Popen(
                [venv_python, daemon_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, # Ignorer stderr ou rediriger vers log file si besoin
                text=True,
                bufsize=1 # Line buffered
            )
            print("✅ Daemon NER lancé.")
        except Exception as e:
            print(f"❌ Echec lancement Daemon : {e}")
            self.daemon_process = None

    def analyze(self, word: str, context: str) -> Dict:
        """
        Orchestration du Pipeline V8 (NER).
        1. Fast Check (Daemon FlauBERT).
        2. Deep Check (Mistral) si ambigu.
        """
        
        # Stage 1: FlauBERT via Daemon
        if self.daemon_process:
            try:
                # Envoyer requête
                payload = json.dumps({"text": context}) + "\n"
                self.daemon_process.stdin.write(payload)
                self.daemon_process.stdin.flush()
                
                # Lire réponse
                response_line = self.daemon_process.stdout.readline()
                if response_line:
                    data = json.loads(response_line)
                    if data.get("status") == "ok":
                        entities = data.get("entities", [])
                        
                        # Check match
                        for ent in entities:
                            if word in ent['word'] or ent['word'] in word:
                                if ent['score'] > 0.85:
                                    return {
                                        "is_proper_noun": True,
                                        "type": ent['entity_group'],
                                        "confidence": ent['score'],
                                        "source": "FlauBERT (Daemon)"
                                    }
                else:
                    raise BrokenPipeError("Daemon sent empty response (crash)")

            except (BrokenPipeError, json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"⚠️ Daemon CamemBERT crashed ({e}). Switching to Mistral-Only mode.")
                print(f"⚠️ Daemon died. Fallback -> Mistral.")
                self.daemon_process = None # Disable completely for this session

        # Stage 2: Mistral (Le Consul) / Fallback
        return self._ask_mistral(word, context)

    def _ask_mistral(self, word: str, context: str) -> Dict:
        """Analyse sémantique profonde via Mistral."""
        # ... (Reste inchangé) ...
        # Copie temporaire pour reference, à remplacer par le vrai appel
        prompt = f"""[INST] Tu es un expert en linguistique.
Analyse le mot "{word}" dans la phrase : "{context}"

Est-ce un NOM PROPRE valide (Personne, Lieu, Organisation) qui doit être préservé ?
Ou est-ce une ERREUR (Coquille, Mot collé, Nom commun mal écrit) ?

Réponds JSON :
{{
  "is_proper_noun": true/false,
  "type": "PER/LOC/ORG/MISC/ERROR",
  "reason": "Explication courte"
}}
[/INST]"""
        try:
            response_text = self.semantic._model(
                prompt, max_tokens=150, temperature=0.0
            )['choices'][0]['text']
            
            is_valid = "true" in response_text.lower() and "false" not in response_text.lower()
            return {
                "is_proper_noun": is_valid,
                "confidence": 0.9,
                "source": "Mistral",
                "raw": response_text
            }
        except Exception:
            return {"is_proper_noun": False, "source": "Mistral (Error)"}

    def close(self):
        """Arrêt propre du daemon."""
        if self.daemon_process:
            self.daemon_process.terminate()

    def __del__(self):
        self.close()
