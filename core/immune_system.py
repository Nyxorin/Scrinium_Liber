import json
import os
import re

class ImmuneSystem:
    """
    Manages the 'Antibodies' (Persistent Blacklist and Correction Rules).
    If a word is identified as a known error (Antigen), it is immediately neutralized (Corrected).
    """

    def __init__(self, antibodies_path="data/knowledge/antibodies.json"):
        self.antibodies_path = antibodies_path
        self.antibodies = self._load_antibodies()

    def _load_antibodies(self):
        if os.path.exists(self.antibodies_path):
            try:
                with open(self.antibodies_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading antibodies: {e}")
                return {}
        return {}

    def save_antibodies(self):
        os.makedirs(os.path.dirname(self.antibodies_path), exist_ok=True)
        with open(self.antibodies_path, 'w', encoding='utf-8') as f:
            json.dump(self.antibodies, f, indent=4, ensure_ascii=False)

    def attack(self, text):
        """
        Applies Antibody rules to the text.
        Returns the sanitized text.
        """
        # 1. Word-level replacements (Fastest)
        # We iterate over the antibodies and apply regex replacement
        # Ideally, we should tokenize the text, but regex is faster for global search/replace.
        
        # To avoid partial matches (replacing 'alko' inside 'alcool'), use \b boundaries.
        cleaned_text = text
        for antigen, antibody in self.antibodies.items():
            # Escape antigen to use in regex
            pattern = r'\b' + re.escape(antigen) + r'\b'
            cleaned_text = re.sub(pattern, antibody, cleaned_text)
            
        return cleaned_text

    def learn_antigen(self, antigen, antibody):
        """
        Learns a new Antibody (Correction Rule).
        ex: learn_antigen("Sommalie", "Somalie")
        """
        if antigen and antibody and antigen != antibody:
            self.antibodies[antigen] = antibody
            self.save_antibodies()
            return True
        return False
