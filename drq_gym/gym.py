import argparse
import sys
import os

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drq_gym.attacker import Attacker
from drq_gym.defender import Defender
from drq_gym.evaluator import Evaluator
from drq_gym.trainer import Trainer
from drq_gym.phantom_client import PhantomClient

class RedQueenGym:
    """
    The Red Queen's Gym: An evolutionary environment for optimizing the OCR cleaning pipeline.
    """
    def __init__(self, model_path: str, knowledge_base: str, blacklist_path: str, corpus_path: str = None):
        self.attacker = Attacker()
        self.defender = Defender(model_path, knowledge_base, blacklist_path)
        self.evaluator = Evaluator()
        self.trainer = Trainer()
        
        # [Phase 20] Phantom Protocol (Bi-Cameral Judge)
        print("👻 Initializing Phantom Protocol (Judge)...")
        self.phantom = PhantomClient()
        
        self.seed_corpus = self._load_corpus(corpus_path)

    def _load_corpus(self, path: str) -> list[str]:
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                # Read lines, strip whitespace, and filter empty lines
                return [line.strip() for line in f if line.strip()]
        
        # Fallback to hardcoded seed if no file provided
        return [
            "L'homme marchait dans la rue sombre.",
            "Il avait un rendez-vous important.",
            "Malko Linge regarda sa montre en or.",
            "La CIA était impliquée dans cette affaire.",
            "C'était une belle journée à Paris."
        ]

    def run_episode(self, episode_id: int):
        print(f"--- Starting Episode {episode_id} ---")
        
        dataset = self.attacker.generate_dataset(self.seed_corpus)
        print(f"Generated {len(dataset)} synthetic samples.")
        
        total_score = 0
        total_perplexity = 0
        
        for i, (noisy, ground_truth) in enumerate(dataset):
            print(f"\nSample {i+1}:")
            print(f"  Input:  '{noisy}'")
            
            corrected = self.defender.clean(noisy)
            print(f"  Output: '{corrected}'")
            
            # 1. Similarity Score (Ground Truth)
            metrics = self.evaluator.evaluate(corrected, ground_truth)
            sim_score = metrics['similarity_score']
            
            # 2. Perplexity Score (Phantom Judge)
            ppl_score = self.phantom.score(corrected)
            
            print(f"  Score:  {sim_score:.4f} | Perplexity: {ppl_score:.2f}")
            
            # Combined Metric: Similarity penalized by High Perplexity (if > 30)
            # If PPL > 30, penalty applies.
            ppl_penalty = max(0, (ppl_score - 20) / 100) # Soft penalty
            final_score = sim_score - ppl_penalty
            
            total_score += final_score
            total_perplexity += ppl_score
            
        avg_score = total_score / len(dataset) if dataset else 0
        avg_ppl = total_perplexity / len(dataset) if dataset else 0
        
        print(f"\nEpisode {episode_id} Avg Score: {avg_score:.4f} | Avg Perplexity: {avg_ppl:.2f}")
        
        current_prompt = self.defender.semantic_corrector.prompt_template
        self.trainer.record_episode(episode_id, current_prompt, avg_score)
        
        return avg_score

def main():
    parser = argparse.ArgumentParser(description="Red Queen's Gym - OCR Optimization")
    parser.add_argument("--model", type=str, required=True, help="Path to LLM model")
    parser.add_argument("--kb", type=str, required=True, help="Path to Knowledge Base (chroma)")
    parser.add_argument("--blacklist", type=str, default="blacklist.json", help="Path to blacklist")
    parser.add_argument("--episodes", type=int, default=1, help="Number of episodes to run")
    parser.add_argument("--corpus", type=str, help="Path to clean corpus (txt file)")
    
    args = parser.parse_args()
    
    gym = RedQueenGym(args.model, args.kb, args.blacklist, args.corpus)
    
    for e in range(1, args.episodes + 1):
        gym.run_episode(e)

if __name__ == "__main__":
    main()
