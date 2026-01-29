import re
from core.dictionary import FrenchDictionary

class Macrophage:
    """
    Bio-mimetic module responsible for 'digesting' structural anomalies.
    Its main job is to split glued words (e.g., 'lhomme', 'dela') that the simple dictionary check misses.
    """

    def __init__(self):
        self.dictionary = FrenchDictionary()
        # Particles that require an apostrophe when used as prefix
        self.elision_particles = {'l', 'd', 'qu', 'm', 't', 's', 'c', 'n', 'j', 'jusqu', 'lor', 'puisqu'}
        self.min_word_length = 3 

    def digest(self, word):
        """
        Attempts to split a glued word into valid components.
        Returns the corrected string (e.g., "l'homme") or the original word if no split found.
        """
        if not word or len(word) < 4:
            return word

        # 1. Check for CamelCase (e.g. "LhommeMarchait")
        if re.search(r'(?<!^)[A-Z]', word) and not word.isupper():
            camel_split = self._split_camel_case(word)
            if camel_split != word:
                return camel_split

        # 2. Dictionary Attack Split
        if not self.dictionary.validate(word):
            split_candidate = self._attempt_split(word)
            if split_candidate:
                return split_candidate

        return word

    def _split_camel_case(self, word):
        """
        Splits CamelCase words (e.g. 'LeChat' -> 'Le Chat').
        """
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', word)

    def _attempt_split(self, word):
        """
        Brute-force split: Check all possible split points.
        """
        n = len(word)
        # Try finding the longest valid split
        for i in range(1, n):
            left = word[:i]
            right = word[i:]

            if len(left) < 1 or len(right) < 2:
                continue

            spacer = " "
            # Check elision
            if left.lower() in self.elision_particles:
                 spacer = "'"
                 # Particle is valid by definition if in list
                 is_valid_left = True
            else:
                is_valid_left = self.dictionary.validate(left)

            if is_valid_left:
                if self.dictionary.validate(right):
                    # Found a valid split. 
                    # Heuristic: If we used an elision, it's very likely correct (l'homme).
                    # If we used a space, we should be careful. 
                    # For now, return the first valid one? 
                    # Or maybe prefer splits where 'left' is longer?
                    # Current loop goes from left=1 to n. So it finds shortest left first.
                    # 'lhomme' -> l + homme. ('l' is short).
                    # 'dela' -> d + ela (ela? non) -> de + la.
                    return f"{left}{spacer}{right}"
        
        return None
