import os
import json
from typing import List, Dict

class Trainer:
    """
    The Trainer orchestrates the evolutionary optimization loop.
    It manages the population of prompts, runs tournaments, and selects the fittest.
    """
    def __init__(self, log_dir: str = "drq_gym/logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.history = []

    def record_episode(self, episode_id: int, prompt: str, score: float):
        """
        Records the results of a training episode.
        """
        record = {
            "episode": episode_id,
            "prompt": prompt,
            "score": score
        }
        self.history.append(record)
        
        # Save to JSON
        with open(os.path.join(self.log_dir, "evolution_history.json"), "a") as f:
            f.write(json.dumps(record) + "\n")

    def run_tournament(self, gym, evolver, seed_prompt: str, generations: int = 3, episodes_per_gen: int = 3) -> str:
        """
        Runs the evolutionary loop.
        1. Generate Population.
        2. Evaluate each candidate.
        3. Select Winner.
        4. Repeat.
        Returns the winning prompt.
        """
        current_best_prompt = seed_prompt
        current_best_score = 0.0

        print(f"🧬 Starting Evolution: {generations} generations...")

        for gen in range(generations):
            print(f"\n--- Generation {gen+1}/{generations} ---")
            
            # 1. Mutate
            population = evolver.evolve_population(current_best_prompt, population_size=3)
            
            gen_results = []
            
            # 2. Evaluate
            for i, prompt in enumerate(population):
                print(f"  Testing Candidate {i+1}...")
                
                # Apply phenotype (prompt) to Defender
                gym.defender.semantic_corrector.prompt_template = prompt 
                
                # Run Episode
                score = gym.run_episode(episode_id=f"{gen+1}-{i+1}")
                
                gen_results.append((prompt, score))
                
                self.record_episode(f"{gen+1}-{i+1}", prompt, score)
            
            # 3. Select
            winner_prompt, winner_score = max(gen_results, key=lambda x: x[1])
            print(f"  🏆 Generation Winner: Score {winner_score:.4f}")
            
            if winner_score > current_best_score:
                current_best_score = winner_score
                current_best_prompt = winner_prompt
                print(f"  🚀 New All-Time Best! ({current_best_score:.4f})")
        
        print(f"\n✨ Evolution Complete. Best Score: {current_best_score:.4f}")
        return current_best_prompt
