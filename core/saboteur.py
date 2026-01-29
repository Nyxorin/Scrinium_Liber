import random
import os
import sys
import json
import logging
from typing import List, Tuple, Dict

class SaboteurAgent:
    """
    The Saboteur Agent (Bmad-style evolved).
    
    Mission: Generate realistic OCR errors strategies to train the Defender.
    Scope: Strictly limited to OCR artifacts (Visual, Structural, Noise). No semantic hallucination.
    DNA: Digital Red Queen (DrQ) - Learns from feedback to optimize attack strategies.
    """
    
    def __init__(self, corpus_path: str = None):
        self.logger = logging.getLogger("SaboteurAgent")
        
        # [Memory] Weights for each strategy (Evolutionary DNA)
        self.memory_path = "data/saboteur_dna.json"
        self.strategy_weights = self._load_dna()
        
        # [Corpus] Real text to sabotage
        self.corpus_lines = []
        self._load_corpus()

        # [Capabilities] Confusion Matrix (The "Mimic" Gene)
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
        
    def _load_dna(self) -> Dict[str, float]:
        """Loads the learned weights for strategies."""
        default_dna = {
            "apostrophe_chaos": 1.0,
            "camel_case": 0.5,
            "digit_contamination": 0.5,
            "visual_noise": 1.0,
            "structural_noise": 0.2,
            "ligature_destruction": 0.5
        }
        
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    dna = json.load(f)
                    # Merge with defaults (in case of new genes)
                    for k, v in default_dna.items():
                        if k not in dna:
                            dna[k] = v
                    return dna
            except Exception:
                pass
        return default_dna

    def save_dna(self):
        """Persists the learned weights."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, 'w') as f:
            json.dump(self.strategy_weights, f, indent=2)

    def _load_corpus(self):
        """Loads all available clean text corpora for real-world simulation."""
        import glob
        corpus_files = glob.glob("*_CLEAN.txt")
        if not corpus_files:
            # Fallback for testing
            return
            
        for c_path in corpus_files:
            try:
                with open(c_path, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if len(line) > 50]
                    self.corpus_lines.extend(lines)
            except Exception:
                pass
        print(f"🦹 Saboteur Agent initialized with {len(self.corpus_lines)} lines of context.")

    # --- STRATEGIES (The Arsenal) ---

    def _inject_apostrophe_chaos(self, text: str) -> str:
        """Simulates the #1 Error: Apostrophe Corruption."""
        if "'" not in text and "’" not in text: return text
        chars = list(text)
        new_chars = []
        for char in chars:
            if char in ["'", "’"]:
                dice = random.random()
                if dice < 0.6: new_chars.append("' ") # Schism
                elif dice < 0.8: new_chars.append("'") # Normalization
                elif dice < 0.9: pass # Missing
                else: new_chars.append(random.choice(['"', '7', ' '])) # Noise
            else:
                new_chars.append(char)
        return "".join(new_chars)

    def _inject_camel_case(self, text: str) -> str:
        """Simulates CamelCase Injection."""
        words = text.split(' ')
        new_words = []
        for word in words:
            if len(word) > 4 and word.isalpha() and random.random() < 0.05:
                char_list = list(word)
                idx = random.randint(1, len(word)-2)
                char_list[idx] = char_list[idx].upper()
                new_words.append("".join(char_list))
            else:
                new_words.append(word)
        return " ".join(new_words)

    def _inject_digit_contamination(self, text: str) -> str:
        """Mappings: u->11, h->4, etc."""
        mappings = {'u': '11', 'h': '4', 'q': '4', 'H': '1', 'l': '1', 'o': '0', 'e': '3', 'a': '4'}
        chars = list(text)
        for i in range(len(chars)):
            if chars[i] in mappings and random.random() < 0.02:
                chars[i] = mappings[chars[i]]
        return "".join(chars)

    def _inject_visual_noise(self, text: str) -> str:
        """Confusion Matrix application."""
        noisy_text = list(text)
        indices = random.sample(range(len(text)), min(int(len(text)*0.05) + 1, len(text)))
        for i in indices:
            char = noisy_text[i]
            if char in self.confusion_matrix:
                options, weights = zip(*self.confusion_matrix[char])
                noisy_text[i] = random.choices(options, weights=weights, k=1)[0]
        return "".join(noisy_text)

    def _inject_structural_noise(self, text: str) -> str:
        """Injects page numbers or headers."""
        if random.random() < 0.5:
            # Page number
            noise = random.choice([f" {random.randint(1, 400)} ", f" - {random.randint(1, 400)} - "])
            pos = random.randint(0, len(text))
            return text[:pos] + noise + text[pos:]
        return text

    # --- MAIN ATTACK LOOP ---

    def attack(self, text: str = None) -> Tuple[str, str, str]:
        """
        Executes a sabotage mission.
        Returns: (trapped_text, ground_truth, strategy_used)
        """
        # 1. Acquire Target
        if text:
            ground_truth = text
        else:
            if not self.corpus_lines:
                return "Erreur Corpus", "Erreur Corpus", "None"
            ground_truth = random.choice(self.corpus_lines)

        # 2. Select Strategy (Evolutionary Selection)
        # We choose one PRIMARY strategy to dominate, but others might mix in slightly?
        # For clear learning, let's pick one dominant strategy.
        strategies = list(self.strategy_weights.keys())
        weights = list(self.strategy_weights.values())
        
        chosen_strat = random.choices(strategies, weights=weights, k=1)[0]
        
        # 3. Execute
        trap = ground_truth
        
        if chosen_strat == "apostrophe_chaos":
            trap = self._inject_apostrophe_chaos(trap)
        elif chosen_strat == "camel_case":
            trap = self._inject_camel_case(trap)
        elif chosen_strat == "digit_contamination":
            trap = self._inject_digit_contamination(trap)
        elif chosen_strat == "visual_noise":
            trap = self._inject_visual_noise(trap)
        elif chosen_strat == "structural_noise":
            trap = self._inject_structural_noise(trap)
        
        # Always mix in a bit of visual noise if it implies robustness?
        # No, keep it pure for attribution.
        
        return trap, ground_truth, chosen_strat

    def learn_from_feedback(self, strategy: str, saboteur_won: bool):
        """
        Reinforcement Learning (DNA Update).
        If Saboteur WON (Defender failed), BOOST the strategy.
        If Saboteur LOST (Defender fixed it), REDUCE the strategy (it's too easy).
        """
        current_weight = self.strategy_weights.get(strategy, 1.0)
        
        if saboteur_won:
            # Good job, this strategy found a crack. Do it more!
            self.strategy_weights[strategy] = min(current_weight * 1.1, 10.0)
            print(f"🧬 Saboteur DNA Evolved: {strategy} is EFFECTIVE -> Weight boosted to {self.strategy_weights[strategy]:.2f}")
        else:
            # This strategy is totally blocked by Defender. Try something else.
            # Don't zero it out (mutation needed), but lower it.
            self.strategy_weights[strategy] = max(current_weight * 0.9, 0.1)
            print(f"🧬 Saboteur DNA Evolved: {strategy} is BLOCKED -> Weight reduced to {self.strategy_weights[strategy]:.2f}")
            
        self.save_dna()

# Alias for backward compatibility if needed, but we prefer SaboteurAgent
Saboteur = SaboteurAgent
