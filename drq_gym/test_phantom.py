import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drq_gym.phantom_client import PhantomClient
import time

def test_phantom():
    print("👻 Initializing Phantom Protocol...")
    client = PhantomClient()
    time.sleep(2) # Warmup

    sentences = [
        "Le chat boit du lait.",        # Fluid
        "Le chat boit du béton.",       # Semantic Weirdness
        "Le cbat boit du laif.",        # Typo
        "Manger pomme je vouloir."      # Grammatically broken
    ]

    print("\n--- Scoring Sentences ---")
    for s in sentences:
        score = client.score(s)
        print(f"'{s}' -> Perplexity: {score:.2f}")

    client.close()
    print("\n✅ Test Complete.")

if __name__ == "__main__":
    test_phantom()
