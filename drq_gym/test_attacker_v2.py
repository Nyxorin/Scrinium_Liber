
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from drq_gym.attacker import Attacker

def test_attacker_v2():
    print("⚔️ Testing Attacker V2 (Historical Re-enactment) ⚔️")
    attacker = Attacker(error_rate=0.05)
    
    samples = [
        "L'homme marchait dans la rue de l'Abbaye.",
        "C'était une provocation inacceptable pour le Département.",
        "Il y avait quelques chaînes rouillées sur la tête du cadavre.",
        "Même les étudiantes de Mogadiscio étaient là.",
        "L'ambassadeur des Etats-Unis regardait la scène avec horreur."
    ]
    
    print(f"\nTest 1: Specific Injections (Force Run)")
    print("-" * 50)
    
    text = "L'homme provoca une scène."
    print(f"Original: {text}")
    print(f"Schism Check: {attacker.inject_apostrophe_chaos(text)}")
    print(f"CamelCase Check: {attacker.inject_camel_case('provocation')}")
    print(f"Digits Check: {attacker.inject_digit_contamination('quelques')}")
    print(f"Accents Check: {attacker.inject_accent_noise('tête de la bête')}")

    print("\nTest 2: Full Pipeline (Randomized)")
    print("-" * 50)
    for i, sample in enumerate(samples):
        print(f"\nSample {i+1}:")
        print(f"ORIG: {sample}")
        # Run multiple times to see different variations
        for j in range(3):
            noisy = attacker.inject_noise(sample)
            print(f"NOISY ({j+1}): {noisy}")

if __name__ == "__main__":
    test_attacker_v2()
