
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from drq_gym.phantom_client import PhantomClient

def investigate_phantom():
    print("👻 Investigating Phantom Protocol Blindness...")
    phantom = PhantomClient()
    
    # Test cases: Good vs Bad
    test_cases = [
        ("Le chat boit du lait.", "Perfect sentence"),
        ("Le cbat boit du laif.", "Typos (Blindness?)"),
        ("Le chat mange de la nourriture.", "Complex perfect"),
        ("Le chat mznge de la nourrifure.", "Complex typos"),
        ("L'homme est grand.", "Perfect short"),
        ("L' homm est grand.", "Schism error")
    ]
    
    print(f"\n{'Sentence':<40} | {'Perplexity':<10} | {'Type'}")
    print("-" * 70)
    
    for text, label in test_cases:
        score = phantom.score(text)
        print(f"{text:<40} | {score:<10.2f} | {label}")

if __name__ == "__main__":
    investigate_phantom()
