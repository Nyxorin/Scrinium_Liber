import requests
import json
import logging
from typing import Dict, Any, Optional

class SandboxArena:
    """
    Client for the SandboxFusion execution environment.
    Handles communication with the local Docker-based sandbox.
    """
    def __init__(self, sandbox_url: str = "http://localhost:8000"):
        self.sandbox_url = sandbox_url.rstrip('/')
        self.logger = logging.getLogger("SandboxArena")

    def check_health(self) -> bool:
        """Checks if the Sandbox server is reachable."""
        try:
            # SandboxFusion usually has a simple root or health endpoint
            # We'll try a basic GET, if it fails we assume down
            response = requests.get(f"{self.sandbox_url}/", timeout=2)
            return response.status_code < 500
        except requests.RequestException:
            return False

    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Executes code within the Sandbox.
        
        Args:
            code: The source code to execute.
            language: 'python', 'cpp', 'java', etc. (supported by SandboxFusion).
        
        Returns:
            Dict containing 'stdout', 'stderr', 'exit_code', 'time', etc.
        """
        payload = {
            "code": code,
            "language": language,
            "timeout": 10,          # 10s timeout default
            "memory_limit": 256,    # 256MB default
        }

        try:
            self.logger.info(f"🚀 Sending code ({language}) to Sandbox...")
            response = requests.post(f"{self.sandbox_url}/run", json=payload, timeout=12)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                self.logger.error(f"Sandbox Error {response.status_code}: {response.text}")
                return {
                    "stdout": "",
                    "stderr": f"Sandbox API Error: {response.text}",
                    "exit_code": -1
                }
                
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to Sandbox: {e}")
            return {
                "stdout": "",
                "stderr": f"Connection Failed: {str(e)}",
                "exit_code": -1
            }

    def cleanup(self):
        """Optional cleanup if session management is needed later."""
        pass
