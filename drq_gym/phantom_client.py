import subprocess
import json
import os
import sys

class PhantomClient:
    """
    Client for the Phantom Protocol (CamemBERT Daemon).
    Acts as a bridge to the isolated process for perplexity scoring.
    """
    def __init__(self):
        self.process = None
        self._start_daemon()

    def _start_daemon(self):
        """Launches the Phantom Daemon in the isolated environment."""
        daemon_path = os.path.join(os.path.dirname(__file__), "phantom_daemon.py")
        venv_python = os.path.join(os.getcwd(), ".ner_env", "bin", "python3")
        
        if not os.path.exists(venv_python):
            print(f"⚠️ Phantom env not found ({venv_python}). Using system python (RISKY).")
            venv_python = sys.executable

        try:
            self.process = subprocess.Popen(
                [venv_python, daemon_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )
            print("👻 Phantom Bridge Established.")
        except Exception as e:
            print(f"❌ Phantom Bridge Failed: {e}")
            self.process = None

    def score(self, text: str) -> float:
        """
        Queries the Phantom for the perplexity score of the text.
        Returns: Perplexity (0.0 to infinity). Lower is better.
        """
        if not self.process:
            return 999.9 # High perplexity if service down

        try:
            payload = json.dumps({"text": text}) + "\n"
            self.process.stdin.write(payload)
            self.process.stdin.flush()
            
            response = self.process.stdout.readline()
            if response:
                data = json.loads(response)
                return data.get("perplexity", 999.9)
            
        except Exception as e:
            print(f"👻 Phantom Communication Error: {e}")
            self.process = None # Reset
            
        return 999.9

    def close(self):
        if self.process:
            self.process.terminate()

    def __del__(self):
        self.close()
