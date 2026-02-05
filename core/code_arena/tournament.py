import logging
import json
import requests
import re
from typing import List, Dict, Any
from .sandbox_client import SandboxArena

class Tournament:
    """
    Manages the Code Tournament between two AI Fighters.
    """
    def __init__(self, fighter_a_url: str, fighter_b_url: str, sandbox_url: str = "http://localhost:8000"):
        self.arena = SandboxArena(sandbox_url)
        self.fighter_a_url = fighter_a_url
        self.fighter_b_url = fighter_b_url
        self.scores = {"A": 0, "B": 0}
        self.logger = logging.getLogger("Tournament")
        
    def _generate_code(self, endpoint: str, challenge: str) -> str:
        """
        Asks the AI Model at 'endpoint' to solve the challenge.
        Expects a llama.cpp compatible server.
        """
        prompt = f"Écris UNIQUEMENT du code Python pour résoudre ce problème:\n{challenge}\n\nAssure toi que le code est complet et fonctionnel. Ne mets pas d'explication, juste le code dans des blocs markdown."
        
        payload = {
            "prompt": prompt,
            "n_predict": 1024,
            "temperature": 0.2, # Low temp for code
            "stop": ["```\\n\\n", "User:", "Observation:", "Explication:"]
        }
        
        try:
            response = requests.post(f"{endpoint}/completion", json=payload, timeout=60)
            if response.status_code == 200:
                content = response.json().get("content", "")
                return self._extract_code_block(content)
            else:
                self.logger.error(f"Fighter Error {response.status_code}: {response.text}")
                return ""
        except Exception as e:
            self.logger.error(f"Fighter Connection Failed: {e}")
            return ""

    def _extract_code_block(self, text: str) -> str:
        """Extracts Python code from Markdown blocks."""
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        # Fallback: check generic block
        pattern_generic = r"```(.*?)```"
        matches_generic = re.findall(pattern_generic, text, re.DOTALL)
        if matches_generic:
            return matches_generic[0].strip()
            
        return text.strip() # Hope for the best

    def run_round(self, challenge_description: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs a single round of combat.
        """
        self.logger.info(f"⚔️ Starting Round: {challenge_description[:50]}...")
        
        # 1. Generation Phase
        code_a = self._generate_code(self.fighter_a_url, challenge_description)
        code_b = self._generate_code(self.fighter_b_url, challenge_description)
        
        if not code_a: self.logger.warning("Fighter A failed to generate code.")
        if not code_b: self.logger.warning("Fighter B failed to generate code.")
        
        # 2. Execution Phase (Sandbox)
        results_a = self._evaluate_solution(code_a, test_cases)
        results_b = self._evaluate_solution(code_b, test_cases)
        
        # 3. Scoring
        score_a = sum(1 for r in results_a if r['passed'])
        score_b = sum(1 for r in results_b if r['passed'])
        
        winner = "Draw"
        if score_a > score_b:
            winner = "A"
            self.scores["A"] += 1
        elif score_b > score_a:
            winner = "B"
            self.scores["B"] += 1
            
        return {
            "challenge": challenge_description,
            "winner": winner,
            "fighter_a": {"code": code_a, "results": results_a, "score": score_a},
            "fighter_b": {"code": code_b, "results": results_b, "score": score_b}
        }

    def _evaluate_solution(self, code: str, test_cases: List[Dict]) -> List[Dict]:
        """Executes the code against multiple test cases."""
        if not code:
            return [{"passed": False, "error": "No Code Generated"}] * len(test_cases)
            
        round_results = []
        for test in test_cases:
            # We append the test case call to the code
            # Assuming the code defines a function usually.
            # But for simplicity, we might ask the model to print the result.
            
            # Smart Injection: Wrap code with a test runner?
            # For now, let's assume the prompt asks for a function 'solution'
            # and we append the print check.
            
            test_appended = f"\\n{code}\\n\\n# Test Runner\\ntry:\\n    print(solution({test['input']}))\\nexcept Exception as e:\\n    print(f'Error: {{e}}')\\n"
            
            sandbox_res = self.arena.execute_code(test_appended, "python")
            
            model_output = sandbox_res.get("stdout", "").strip()
            stderr = sandbox_res.get("stderr", "")
            
            expected = str(test['expected'])
            passed = (model_output == expected)
            
            round_results.append({
                "input": test['input'],
                "expected": expected,
                "actual": model_output,
                "error": stderr,
                "passed": passed
            })
            
        return round_results
