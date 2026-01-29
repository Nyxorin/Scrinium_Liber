
import re
import json

class RegexGenerator:
    """
    Phase 32: The Logic Forge.
    Uses an LLM to deduce Python Regex rules from specific Error->Correction examples.
    """
    def __init__(self, model_wrapper):
        """
        Args:
            model_wrapper: Instance of Saboteur or SemanticCorrector (must have .model or .generate)
                           We reuse the Arena's loaded model to save RAM.
        """
        self.model_wrapper = model_wrapper

    def deduce_rule(self, bad_segment: str, good_segment: str) -> str:
        """
        Asks the LLM to write a regex that turns bad_segment into good_segment.
        """
        
        prompt = f"""[INST] You are a Python Regex Expert.
Task: Write a python `re.sub` pattern to fix a specific OCR error.

Example:
Input: "L'ho mme"
Target: "L'homme"
Reasoning: Space inside "homme" after apostrophe.
Regex: r"\\bL'ho mme\\b", "L'homme"

Current Task:
Input: "{bad_segment}"
Target: "{good_segment}"

Reply ONLY with a JSON object containing the 'pattern' and 'replacement'.
Format: {{ "pattern": "regex_here", "replacement": "replacement_string" }}
Do not explain. [/INST]
"""
        # We assume model_wrapper has a generate or similar. 
        # If it's the Saboteur class, it has direct access to self.model (Llama)
        # We need to handle the raw Llama object or the wrapper.
        
        # Checking if it's a llama_cpp.Llama object or wrapper
        llm = self.model_wrapper.model if hasattr(self.model_wrapper, 'model') else self.model_wrapper
        
        output = llm(
            prompt, 
            max_tokens=100, 
            stop=["[/INST]", "Input:"], 
            temperature=0.1
        )
        
        text = output['choices'][0]['text'].strip()
        
        # Attempt minimal parsing
        try:
            # Find JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = text[start:end]
                rule = json.loads(json_str)
                return rule
        except:
            return None
        return None

    def validate_rule(self, rule: dict, bad: str, good: str) -> bool:
        """
        Sandboxes the regex to ensure it works and isn't dangerous.
        """
        if not rule or 'pattern' not in rule or 'replacement' not in rule:
            return False
            
        try:
            pat = rule['pattern']
            rep = rule['replacement']
            
            # 1. Does it fix the error?
            result = re.sub(pat, rep, bad)
            if result != good:
                return False
                
            # 2. Is it too broad? (Sanity check)
            # If pattern is just ".", it's bad.
            if len(pat) < 3:
                return False
                
            return True
        except:
            return False
