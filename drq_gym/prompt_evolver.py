import random
from typing import List

class PromptEvolver:
    """
    Implements a simple Genetic Algorithm to evolve the System Prompt.
    Methods:
    - mutate(prompt): Randomly alters instructions (e.g. changing 'Standard' to 'Strict').
    - crossover(prompt_a, prompt_b): Mixes two prompts (Not implemented for text yet).
    """
    def __init__(self):
        self.mutations = [
            # Tactic 1: Safety Enforcement
            ("Translate", "Do not translate"),
            ("Rewording", "Do not rephrase"),
            # Tactic 2: Detail Level
            ("Correct the text", "Correct the OCR errors while preserving style"),
            ("Output only the corrected text", "Return strictly the corrected segment"),
            # Tactic 3: Hallucination Prevention
            ("Be creative", "Be conservative"),
            ("Infer missing words", "Do not guess missing words"),
            # Tactic 4: Specific OCR hints
            ("", " Pay attention to 'l' vs '1' errors."),
            ("", " Watch out for 'MISSION IMPOSSIBLE' headers."),
            ("", " Do not merge words.")
        ]

    def mutate(self, prompt: str) -> str:
        """
        Applies a random mutation to the prompt.
        """
        mutation = random.choice(self.mutations)
        old_phrase, new_phrase = mutation
        
        if old_phrase in prompt:
            # Substitution
            return prompt.replace(old_phrase, new_phrase, 1)
        else:
             # Addition (Append instruction)
             return prompt + new_phrase
    
    def evolve_population(self, seed_prompt: str, population_size: int = 5) -> List[str]:
        """
        Generates a population of mutated prompts from a seed.
        """
        population = [seed_prompt] # Keep the original
        for _ in range(population_size - 1):
            mutant = self.mutate(seed_prompt)
            # Chance for double mutation
            if random.random() < 0.3:
                mutant = self.mutate(mutant)
            population.append(mutant)
        return population
