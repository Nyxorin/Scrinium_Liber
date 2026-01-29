import argparse
import sys
import os

# Create evolution script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drq_gym.gym import RedQueenGym
from drq_gym.prompt_evolver import PromptEvolver
from drq_gym.trainer import Trainer

def main():
    parser = argparse.ArgumentParser(description="Red Queen's Evolution - Prompt Optimization")
    parser.add_argument("--model", type=str, required=True, help="Path to LLM model")
    parser.add_argument("--kb", type=str, required=True, help="Path to Knowledge Base (chroma)")
    parser.add_argument("--blacklist", type=str, default="blacklist.json", help="Path to blacklist")
    parser.add_argument("--corpus", type=str, help="Path to clean corpus (txt file)")
    parser.add_argument("--generations", type=int, default=3, help="Number of generations")
    
    args = parser.parse_args()
    
    gym = RedQueenGym(args.model, args.kb, args.blacklist, args.corpus)
    evolver = PromptEvolver()
    trainer = Trainer() # Replaces the gym's internal trainer with this orchestrator
    
    # Get initial seed prompt
    seed_prompt = gym.defender.semantic_corrector.prompt_template
    
    # Run Tournament
    best_prompt = trainer.run_tournament(gym, evolver, seed_prompt, generations=args.generations)
    
    print("\n\n🏆 Winning Prompt:")
    print("--------------------------------------------------")
    print(best_prompt)
    print("--------------------------------------------------")
    
    # Save to file
    with open("drq_gym/winning_prompt.txt", "w") as f:
        f.write(best_prompt)

if __name__ == "__main__":
    main()
