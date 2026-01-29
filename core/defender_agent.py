import logging
import subprocess
import json
import os
import sys
import time
from typing import Dict, List, Optional

class DefenderAgent:
    """
    Agent 'Defender' (Phase 29).
    Wraps SemanticCorrector in an isolated Daemon Process.
    Ensures robustness: If LLM crashes, the Daemon is restarted automatically.
    """
    
    def __init__(self, model_path: str = None):
        self.logger = logging.getLogger("DefenderAgent")
        self.daemon_process = None
        self.model_path = model_path
        self._start_daemon()

    def _start_daemon(self):
        """Launches the Defender Daemon process."""
        daemon_path = os.path.join(os.path.dirname(__file__), "defender_daemon.py")
        
        # We use sys.executable (same env as Orchestrator)
        python_exe = sys.executable
        
        env = os.environ.copy()
        if self.model_path:
            env["DEFENDER_MODEL_PATH"] = self.model_path

        try:
            print(f"🛡️ Launching Defender Daemon...")
            self.daemon_process = subprocess.Popen(
                [python_exe, daemon_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr, # Redirect stderr to main stderr for visibility
                text=True,
                bufsize=1, # Line buffered
                env=env
            )
            
            # [Phase 36] Handshake: Wait for "ready" signal from Daemon
            ready_line = self.daemon_process.stdout.readline()
            if ready_line:
                try:
                    ready_data = json.loads(ready_line)
                    if ready_data.get("status") == "ready":
                         print("✅ Defender Agent: Daemon signaled READY.")
                except:
                    pass
            
            response = self.send_command("ping")
            if response and response.get("status") == "ok":
                print("✅ Defender Agent CONNECTED to Daemon.")
            else:
                print("⚠️ Defender Agent: Connection Failed (Handshake).")
                
        except Exception as e:
            print(f"❌ Failed to launch Defender Daemon: {e}")
            self.daemon_process = None

    def send_command(self, command: str, payload: dict = None) -> Optional[dict]:
        """Sends a JSON command to the daemon and waits for JSON response."""
        if not self.daemon_process:
            print("⚠️ Daemon not running, restarting...")
            self._start_daemon()
            if not self.daemon_process:
                return None

        req = {"command": command}
        if payload:
            req.update(payload)
            
        try:
            # Write
            json_req = json.dumps(req)
            self.daemon_process.stdin.write(json_req + "\n")
            self.daemon_process.stdin.flush()
            
            # Read
            response_line = self.daemon_process.stdout.readline()
            if not response_line:
                raise BrokenPipeError("Daemon sent empty response (crash?)")
                
            return json.loads(response_line)
            
        except (BrokenPipeError, json.JSONDecodeError, Exception) as e:
            print(f"❌ Error communicating with Defender Daemon: {e}")
            print("🔄 Triggering Restart...")
            self.close()
            self._start_daemon()
            # Retry once?
            return None

    def correct_segment(self, text: str, **kwargs) -> str:
        """Public API matching SemanticCorrector."""
        payload = {"text": text}
        payload.update(kwargs)
        resp = self.send_command("correct_segment", payload)
        if resp and resp.get("status") == "ok":
            return resp.get("data")
        else:
            return text # Fallback to original if failure

    def save_stats(self):
        """Triggers the daemon to save usage stats."""
        self.send_command("save_stats")

    def close(self):
        """Clean shutdown."""
        if self.daemon_process:
            try:
                self.daemon_process.terminate()
                self.daemon_process.wait(timeout=2)
            except:
                self.daemon_process.kill()
            self.daemon_process = None

    def __del__(self):
        self.close()
