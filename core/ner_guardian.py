import re
from typing import List

class NerGuardian:
    """
    Guardian Contextuel (Phase 3 Brainstorming).
    Protects Named Entities (Proper Nouns, Titles) from modifications.
    Used by the Analyst to filter unsafe rules, and by the Corrector to block safe-guards.
    """

    def __init__(self):
        self.titles = {"M.", "Mme", "Mlle", "Dr", "Pr", "Me", "St", "Ste"}

    def is_safe_to_touch(self, word: str, context_before: str = "") -> bool:
        """
        Determines if a word is 'safe' to correct.
        Returns False if it looks like a Named Entity (Protected).
        """
        word = word.strip()
        if not word:
            return True

        # 1. Title Protection (Context)
        # If preceded by a Title, it's a Proper Noun (e.g., M. Dient)
        if context_before.strip() in self.titles:
            return False

        # 2. Capitalization Protection
        # If it starts with a Capital letter, assume it's a Named Entity.
        # Edge Case: Start of sentence. 
        # For safety in the 'Analyst' context (creating regexes), we are conservative:
        # We NEVER create a regex that modifies a Capitalized word implicitly.
        if word[0].isupper():
            return False

        # 3. All Caps (Acronyms)
        if word.isupper() and len(word) > 1:
            return False

        return True

    def scan_for_entities(self, text: str) -> List[str]:
        """Returns a list of detected entities in the text."""
        entities = []
        words = text.split()
        for i, word in enumerate(words):
            context = words[i-1] if i > 0 else ""
            if not self.is_safe_to_touch(word, context):
                entities.append(word)
        return entities
