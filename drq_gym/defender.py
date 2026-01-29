import sys
import os
import re

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from correctors.semantic_corrector import SemanticCorrector
from correctors.deterministic_corrector import DeterministicCorrector
from core.immune_system import ImmuneSystem

class Defender:
    """
    The Defender processes the input text using the Scrinium Liber pipeline.
    It wraps the existing correctors.
    """
    def __init__(self, model_path: str, knowledge_base: str, blacklist_path: str):
        # SemanticCorrector initializes its own knowledge manager internally or via globals
        # We only pass the model path.
        self.semantic_corrector = SemanticCorrector(model_path)
        self.deterministic_corrector = DeterministicCorrector()
        self.immune_system = ImmuneSystem(blacklist_path)

    def clean(self, text: str) -> str:
        """
        Runs the cleaning pipeline on the text.
        """
        # 1. Deterministic
        cleaned = self.deterministic_corrector.correct(text)
        
        # 2. Immune System (Process/Attack)
        # The 'attack' method applies the blacklist antibody rules
        cleaned = self.immune_system.attack(cleaned)
        
        # 3. Semantic (only if needed/configured)
    # 3. Semantic (only if needed/configured)
        needs_correction = False
        if self.semantic_corrector.dictionary:
             # Check for unknown words using simple regex splitting
             for word in re.findall(r"\w+", cleaned):
                 if not self.semantic_corrector.dictionary.validate(word):
                     needs_correction = True
                     break
             
             # [Typos] Check for missing spaces before double punctuation
             if not needs_correction:
                 if re.search(r'[a-zA-Z0-9à-ÿÀ-Ÿ][\?\!\:\;]', cleaned):
                      needs_correction = True
        else:
             needs_correction = True # Fallback if no dictionary

        if needs_correction:
             corrected = self.semantic_corrector.correct_segment(cleaned)
        else:
             corrected = cleaned

        final = corrected
        
        return final

    def update_prompt(self, new_prompt: str):
        """
        Updates the prompt used by the SemanticCorrector.
        """
        self.semantic_corrector.update_prompt_template(new_prompt)
