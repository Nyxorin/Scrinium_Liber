import sys
import os

# Ensure we can find core modules when running as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import difflib
import json
import re
from core.ner_guardian import NerGuardian

class AnalystAgent:
    """
    Agent 'Analyst' (Phase 3 Brainstorming).
    Observes the Arena matches (Trap vs Original) to infer 'SmartRules' for correction.
    Does NOT modify text directly. Outputs Logic.
    
    Inference Logic: (First Principles)
    1. Detects Difference (Visual/OCR shift).
    2. Checks Safety (NER Guardian).
    3. Generates Conditional Rule (Regex + Dictionary Check).
    """

    def __init__(self):
        self.guardian = NerGuardian()
        self.inferred_rules = []
        
    def analyze_match(self, trap_sentence: str, original_sentence: str) -> dict:
        """
        Compares Trap vs Original to deduce a rule.
        Returns a 'SmartRule' dict or None.
        """
        # 1. Identify the Diff
        # Simple word-by-word comparison for now (assuming structure is preserved)
        trap_words = trap_sentence.split()
        orig_words = original_sentence.split()
        
        if len(trap_words) != len(orig_words):
            # Structural drift (words added/removed) -> Too complex for basic analyst
            return None
            
        diffs = []
        for t_word, o_word in zip(trap_words, orig_words):
            if t_word != o_word:
                # We found an error!
                # Identify context
                idx = trap_words.index(t_word)
                context_before = trap_words[idx-1] if idx > 0 else ""
                
                rule = self._infer_single_rule(t_word, o_word, context_before)
                if rule:
                    diffs.append(rule)
                    
        return diffs

    def _infer_single_rule(self, trap_word: str, orig_word: str, context: str) -> dict:
        """
        Deduces the rule to transform trap_word -> orig_word.
        """
        # Axiom 1: Error is Visual.
        # Check if length is similar
        if abs(len(trap_word) - len(orig_word)) > 2:
            return None # Not an OCR error, maybe semantic change
            
        # Axiom 2: NER Protection.
        # If the Original was a Named Entity, we must be VERY careful.
        is_entity = not self.guardian.is_safe_to_touch(orig_word, context)
        
        # Determine the pattern
        # Naive approach: Find the char difference
        # Example: dient -> client (d -> cl)
        # Sequence Matcher to find the 'opcode'
        s = difflib.SequenceMatcher(None, trap_word, orig_word)
        opcodes = s.get_opcodes()
        
        # We look for 'replace' ops
        pattern_in = ""
        pattern_out = ""
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'replace':
                pattern_in = trap_word[i1:i2]
                pattern_out = orig_word[j1:j2]
                break # Only handle single error per word for now
                
        if pattern_in and pattern_out:
            # Create SmartRule
            rule = {
                "type": "SmartRule",
                "trigger_word": trap_word,  # The specific word (micro-regex)
                "correction": orig_word,
                "pattern_in": pattern_in,   # The snippet (d)
                "pattern_out": pattern_out, # The snippet (cl)
                "conditions": [
                    "dictionary_check_required", # Hybrid Rule
                ]
            }
            
            if is_entity:
                # If target is entity, add protection warning
                rule["conditions"].append("is_named_entity")
                rule["safety_warning"] = "Target is Protected Entity. Rule specific to this instance."
            
            self.inferred_rules.append(rule)
            return rule
            
        return None

if __name__ == "__main__":
    analyst = AnalystAgent()
    # Test Scene from Role Playing
    trap = "Le dient a signé."
    orig = "Le client a signé."
    
    print("Analying Match...")
    rules = analyst.analyze_match(trap, orig)
    print(json.dumps(rules, indent=2, ensure_ascii=False))
