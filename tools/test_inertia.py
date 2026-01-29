
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from correctors.semantic_corrector import SemanticCorrector

print("--- TEST PROTOCOLE V5.1 : INERTIE ---")

# On force un faux modèle ou on utilise le modèle réel s'il est là
# L'inertie est dans _is_safe_correction, donc on peut tester sans modèle LLM actif
# en appelant directement la méthode protégée.

semantic = SemanticCorrector() 
if not semantic.dictionary:
    print("ERREUR: Dictionnaire non chargé.")
    sys.exit(1)

test_cases = [
    # Cas 1 : Le mot original est valide, la correction propose un synonyme (DOIT ETRE REJETÉ)
    {
        "orig": "Les miliciens gardaient la porte.",
        "corr": "Les militaires gardaient la porte.", # miliciens -> militaires (trop différent)
        "expect": False
    },
    # Cas 2 : Le mot original est valide, la correction est une modif mineure (PEUT PASSER ?)
    # cheri -> chéri. 'cheri' n'est PAS valide (pas d'accent).
    # Mais si l'original était "chéri" et qu'on propose "cheri" -> Rejet (dégradation)
    {
        "orig": "Mon pauvre chéri est malade.",
        "corr": "Mon pauvre cheri est malade.",
        "expect": False # chéri est valide, cheri ne l'est pas ou est une dégradation
    },
    # Cas 3 : Correction valide d'un mot invalide (DOIT PASSER)
    {
        "orig": "Les militiens sont là.", # militiens n'existe pas
        "corr": "Les miliciens sont là.",
        "expect": True
    },
    # Cas 4 : Hallucination totale
    {
        "orig": "Il mangea une pomme.",
        "corr": "Il mangea une poire.", # pomme est valide -> poire (trop différent)
        "expect": False 
    }
]

print(f"\n🧪 Lancement des {len(test_cases)} tests d'inertie...\n")

success_count = 0
for i, case in enumerate(test_cases):
    print(f"Test {i+1}: '{case['orig']}' -> '{case['corr']}")
    is_safe = semantic._is_safe_correction(case['orig'], case['corr'])
    
    status = "✅ PASS" if is_safe == case['expect'] else "❌ FAIL"
    print(f"   Attendue: {case['expect']} | Obtenue: {is_safe} -> {status}")
    
    if is_safe == case['expect']:
        success_count += 1
    print("-" * 40)

print(f"\nRésultat: {success_count}/{len(test_cases)}")
if success_count == len(test_cases):
    print("🏆 TOUS LES TESTS D'INERTIE SONT PASSÉS")
else:
    print("⚠️ ECHEC DE CERTAINS TESTS")
