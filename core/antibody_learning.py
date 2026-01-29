
import json
import os
import re
from core.immune_system import ImmuneSystem
from core.dictionary import FrenchDictionary

class AntibodyLearner:
    """
    Analyzes Arena matches to automatically update the Immune System.
    - Learns new Antibodies (Blacklist) from Hallucinations.
    - Learns new WhiteList entries from successful Inertia defenses.
    """
    
    def __init__(self):
        self.immune_system = ImmuneSystem()
        self.dictionary = FrenchDictionary()
        self.whitelist_path = "data/knowledge/whitelist.json"
        
    def learn_from_failures(self, trap: str, defense: str):
        """
        [Phase 28] Single-shot learning from a failed Gym duel.
        Input: the trap text and the failed defense text.
        """
        # Logic adapted from learn_from_arena but for single instance
        trap_words = set(re.findall(r'\w+', trap.lower()))
        def_words = set(re.findall(r'\w+', defense.lower()))
        
        added_words = def_words - trap_words
        
        for word in added_words:
            if len(word) > 3:
                # If word is NOT in dictionary -> It's likely a hallucination (or English)
                if not self.dictionary.validate(word):
                    # It's a toxic hallucination!
                    success = self.immune_system.learn_antigen(word, "[BLOCKED]")
                    if success:
                        print(f"   💉 Generated Antibody for toxic word: '{word}'")

    def learn_from_arena(self, arena_history):
        """
        Input: List of dicts from Arena.history
        [{'round': 1, 'type': '..', 'trap': '..', 'defense': '..', 'winner': '..'}]
        """
        print("\n🧠 Antibody Learning System Active...")
        new_antibodies = 0
        new_whitelist = 0
        
        for entry in arena_history:
            trap = entry['trap']
            defense = entry['defense']
            rule = entry['type']
            winner = entry['winner']
            
            # 1. DETECT HALLUCINATIONS (Saboteur Wins)
            if winner == "Saboteur":
                # If Defender changed the text, check if it introduced a non-existent word
                # diff logic is needed here.
                # Simplification: Check words in Defense not in Trap.
                
                trap_words = set(re.findall(r'\w+', trap.lower()))
                def_words = set(re.findall(r'\w+', defense.lower()))
                
                added_words = def_words - trap_words
                
                for word in added_words:
                    if len(word) > 3:
                        # If word is NOT in dictionary -> It's likely a hallucination (or English)
                        if not self.dictionary.validate(word):
                            # It's a toxic hallucination!
                            # We learn to Block this transition? 
                            # Or just blacklist the word?
                            # For now: Blacklist the word.
                            success = self.immune_system.learn_antigen(word, "[BLOCKED]")
                            if success:
                                print(f"   💉 Generated Antibody for toxic word: '{word}'")
                                new_antibodies += 1
            
            # 2. REINFORCE INERTIA (Defender Wins)
            elif winner == "Defender":
                if "Pseudo-Typo" in rule:
                    # The Trap contained a tricky valid word (e.g. "Somme").
                    # Defender kept it. Good job.
                    # Let's whitelist this word to be sure we never correct it in future.
                    
                    # Identify the "tricky" word? 
                    # Hard without knowing which word was the trap.
                    # But we know the whole sentence was preserved.
                    # We can whitelist all valid words in the sentence?
                    # Too broad.
                    
                    # Refined strategy: If we could identify the target word from Saboteur...
                    # Current Saboteur doesn't output metadata.
                    # We skip for now unless we can be precise.
                    pass
                    
        print(f"🧠 Learning Complete. New Antibodies: {new_antibodies}. New Whitelist: {new_whitelist}")
