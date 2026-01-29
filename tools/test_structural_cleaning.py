
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from correctors.deterministic_corrector import DeterministicCorrector

print("--- TEST PROTOCOLE PHASE 10 : NETTOYAGE STRUCTUREL ---")

corrector = DeterministicCorrector()

test_cases = [
    {
        "name": "Numéro de page isolé",
        "input": "Texte avant.\n123\nTexte après.",
        "expect": "Texte avant.\nTexte après."
    },
    {
        "name": "Indicateur 'Page X'",
        "input": "Chapitre 1\nPage 45\nIl était une fois...",
        "expect": "Chapitre 1\nIl était une fois..."
    },
    {
        "name": "Nombre dans une phrase (Ne doit pas être supprimé)",
        "input": "Il a 25 ans.",
        "expect": "Il a 25 ans."
    }
]

print(f"\n🧪 Lancement des {len(test_cases)} tests structurels...\n")

success_count = 0
for i, case in enumerate(test_cases):
    print(f"Test {i+1} [{case['name']}]:")
    result = corrector.correct(case['input'])
    
    # On normalise les sauts de ligne pour la comparaison
    result = result.strip()
    expect = case['expect'].strip()
    
    status = "✅ PASS" if result == expect else "❌ FAIL"
    print(f"   Input: {case['input'].replace(chr(10), ' | ')}")
    print(f"   Result: {result.replace(chr(10), ' | ')}")
    print(f"   Status: {status}")
    
    if result == expect:
        success_count += 1
    print("-" * 40)

print(f"\nRésultat: {success_count}/{len(test_cases)}")
if success_count == len(test_cases):
    print("🏆 TESTS STRUCTURELS RÉUSSIS")
else:
    print("⚠️ ECHEC DE CERTAINS TESTS")
