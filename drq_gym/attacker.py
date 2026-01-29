import random
import json
from typing import List, Tuple

class Attacker:
    """
    The Attacker generates synthetic OCR errors to create a training dataset.
    V2 Strategy: "The Mimic" - Uses real error typology from project logs.
    tactics:
    - Confusion Matrix (Weighted)
    - Structural Noise (Page numbers, Headers)
    - Apostrophe Corruption
    - Word Fusion/Splitting
    """
    def __init__(self, error_rate: float = 0.05):
        self.error_rate = error_rate
        
        # 1. Confusion Matrix (Based on ANALYSE_FINALE_ERREURS.txt)
        # Structure: char -> [(replacement, weight)]
        self.confusion_matrix = {
            'l': [('1', 0.4), ('I', 0.3), ('|', 0.1), ('!', 0.1)],
            '1': [('l', 0.5), ('I', 0.3)],
            'm': [('rn', 0.6), ('ni', 0.2), ('nn', 0.1)],
            'rn': [('m', 0.8)],
            'q': [('4', 0.5), ('9', 0.2)],
            '4': [('q', 0.4), ('A', 0.2)],
            '0': [('O', 0.5), ('o', 0.3)],
            'O': [('0', 0.6), ('Q', 0.2)],
            'c': [('e', 0.4), ('o', 0.2)],
            'e': [('c', 0.3), ('o', 0.2), ('é', 0.1)],
            'a': [('à', 0.1), ('e', 0.2)],
            't': [('f', 0.3), ('l', 0.2)],
            'f': [('t', 0.4)],
            '.': [(',', 0.3)],
            ',': [('.', 0.3)],
            '\'': [(' ', 0.3), ('"', 0.1)]
        }

        # 2. Structural Noise Patterns
        self.headers = [
            "MISSION IMPOSSIBLE",
            "CHAPITRE",
            "SAS",
            "GERARD DE VILLIERS"
        ]

    def _get_weighted_choice(self, options: List[Tuple[str, float]]) -> str:
        """Selects an option based on weights."""
        choices, weights = zip(*options)
        return random.choices(choices, weights=weights, k=1)[0]

    def inject_apostrophe_chaos(self, text: str) -> str:
        """
        Simulates the #1 Error (94% of cases): Apostrophe Corruption.
        Types:
        - "Schism": l' homme (Detached)
        - "Straight": l'homme (Instead of typographic ’)
        - "Missing": lhomme
        - "Noise": l"homme, l7homme
        """
        if "'" not in text and "’" not in text:
            return text
            
        # Target both types of apostrophes
        chars = list(text)
        new_chars = []
        
        for i, char in enumerate(chars):
            if char in ["'", "’"]:
                dice = random.random()
                if dice < 0.6: 
                    # Type 1: The "Schism" (Detached) - l' homme
                    new_chars.append("' ") 
                elif dice < 0.8:
                    # Type 2: Straight Apostrophe (Normalization failure)
                    new_chars.append("'")
                elif dice < 0.9:
                    # Type 3: Missing (Fusion) - lhomme
                    pass 
                else:
                    # Type 4: Noise - l"homme, l7homme
                    new_chars.append(random.choice(['"', '7', ' ']))
            else:
                new_chars.append(char)
                
        return "".join(new_chars)

    def inject_camel_case(self, text: str) -> str:
        """
         Simonulates Category #2 (~4%): CamelCase Injection.
         ex: socialisatiOn, PrOvoquants
        """
        words = text.split(' ')
        new_words = []
        for word in words:
            if len(word) > 4 and word.isalpha() and random.random() < 0.05: # 5% of long words
                # Inject a capital letter randomly
                char_list = list(word)
                idx = random.randint(1, len(word)-2) # Don't touch first/last
                char_list[idx] = char_list[idx].upper()
                new_words.append("".join(char_list))
            else:
                new_words.append(word)
        return " ".join(new_words)

    def inject_digit_contamination(self, text: str) -> str:
        """
        Simulates Category #3 (~1.3%): Digit/Symbol Contamination.
        Mappings: u->11, h->4, q->4, H->1
        """
        mappings = {
            'u': '11', 'h': '4', 'q': '4', 'H': '1', 
            'l': '1', 'o': '0', 'e': '3', 'a': '4'
        }
        chars = list(text)
        for i in range(len(chars)):
            if chars[i] in mappings and random.random() < 0.02: # Rare
                chars[i] = mappings[chars[i]]
        return "".join(chars)

    def inject_accent_noise(self, text: str) -> str:
        """
        Simulates Category #4 (~0.2%): Accent Swaps.
        tête -> tète, chaîne -> chçne
        """
        replacements = {
            'ê': 'è', 'î': 'i', 'â': 'a', 'é': 'e', 'è': 'é', 
            'ç': 'c', 'à': 'a', 'ù': 'u'
        }
        chars = list(text)
        for i in range(len(chars)):
            if chars[i] in replacements and random.random() < 0.1:
                chars[i] = replacements[chars[i]]
        return "".join(chars)

    def inject_page_numbers(self, text: str) -> str:
        """
        Injects isolated page numbers or artifacts.
        ex: "la voi 45 ture"
        """
        if random.random() < 0.1: # 10% chance per segment
            noise = random.choice([
                f" {random.randint(1, 400)} ",
                f" - {random.randint(1, 400)} - ",
                f" [{random.randint(1, 400)}] "
            ])
            # Insert at random position
            pos = random.randint(0, len(text))
            return text[:pos] + noise + text[pos:]
        return text
    
    def inject_header(self, text: str) -> str:
        """
        Injects a repetitive header.
        ex: "Il disait MISSION IMPOSSIBLE que..."
        """
        if random.random() < 0.05: # 5% chance
            header = random.choice(self.headers)
            pos = random.randint(0, len(text))
            return text[:pos] + f" {header} " + text[pos:]
        return text

    def destroy_ligatures(self, text: str) -> str:
        """
        Entropie ligatures: œ -> Œ, M.
        """
        text = text.replace("œ", random.choice(["Œ", "oe", "M"]))
        text = text.replace("æ", random.choice(["ae", "a"]))
        return text

    def inject_noise(self, text: str) -> str:
        """
        Injects synthetic OCR errors into the text using Mimic strategies.
        """
        # 1. Structural Noise (Aggressive)
        text = self.inject_page_numbers(text)
        text = self.inject_header(text)
        
        # 2. Linguistic Noise (Historical Re-enactments)
        # Probabilities based on VERITE_SUR_LES_ERREURS.md
        
        # Priority 1: Apostrophes (94% of errors)
        # We apply this aggressively if apostrophes exist
        text = self.inject_apostrophe_chaos(text)
        
        # Priority 2: CamelCase (4% of errors)
        if random.random() < 0.2: # Apply to 20% of segments to simulating popping up
            text = self.inject_camel_case(text)
            
        # Priority 3: Digit Contamination (1.3%)
        if random.random() < 0.1:
            text = self.inject_digit_contamination(text)

        # Priority 4: Accents (0.2%)
        if random.random() < 0.05:
            text = self.inject_accent_noise(text)
            
        text = self.destroy_ligatures(text)

        # 3. Char-level Noise (Confusion Matrix)
        noisy_text = list(text)
        n_errors = int(len(text) * self.error_rate)
        
        # Don't error too much on short segments
        if n_errors == 0 and random.random() < 0.3:
            n_errors = 1

        indices = random.sample(range(len(text)), min(n_errors, len(text)))

        for i in indices:
            char = noisy_text[i]
            if char in self.confusion_matrix:
                # Weighted substitution
                noisy_text[i] = self._get_weighted_choice(self.confusion_matrix[char])
            elif random.random() < 0.1:
                # Occasional random deletion for non-matrix chars
                 noisy_text[i] = ""
        
        return "".join(noisy_text)

    def generate_dataset(self, text_segments: List[str]) -> List[Tuple[str, str]]:
        """
        Generates pairs of (noisy_text, ground_truth).
        """
        dataset = []
        for segment in text_segments:
            noisy = self.inject_noise(segment)
            dataset.append((noisy, segment))
        return dataset
