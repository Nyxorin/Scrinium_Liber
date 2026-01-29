import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from correctors.semantic_corrector import SemanticCorrector

def run_tests():
    print("Initialize Semantic Corrector...")
    try:
        corrector = SemanticCorrector()
    except Exception as e:
        print(f"Failed to init: {e}")
        return

    test_cases = [
        # Hallucination Case (Previously produced "A quoi pensez-vous?...")
        {
            "input": "Kathleen se taisait les yeux baissés. Le diplomate fit brusquement demi-tour, rappelé par un cri &une des fillettes.",
            "description": "Risk of Hallucination (Dialogue insertion)"
        },
        # Good Correction Case
        {
            "input": "-âcher ma mort. On ne meurt qu'une fois, monsieur rambassadeur.",
            "description": "Fragment correction (acheter, ambassadeur)"
        },
        # OCR Noise Case
        {
            "input": "Les hom~mes sont là.",
            "description": "OCR Noise Removal"
        },
        # Complete Hallucination Risk (Empty/Nonsense input)
        {
            "input": "zorglub",
            "description": "Nonsense word"
        }
    ]
    
    for case in test_cases:
        print("\n" + "="*50)
        print(f"TEST: {case['description']}")
        print(f"INPUT: {case['input']}")
        result = corrector.correct_segment(case['input'])
        print(f"OUTPUT: {result}")
        
        # Check Safety explicitly here to see debug output if any
        # (The class already prints ⚠️ if rejected, but let's confirm validity)
        safe = corrector._is_safe_correction(case['input'], result)
        print(f"SAFE CHECK: {'✅ Passed' if safe else '❌ Failed (Would be rejected)'}")

if __name__ == "__main__":
    run_tests()
