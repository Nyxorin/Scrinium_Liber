import sys
import os

# Ajout du root au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ner_agent import NERAgent

def test_ner_agent():
    print("🏗️ Initialisation de l'Agent NER (CamemBERT + Mistral)...")
    try:
        agent = NERAgent(use_flaubert=True)
    except Exception as e:
        print(f"❌ Erreur init: {e}")
        return

    test_cases = [
        ("Malko", "Malko regarda la mer rouge."),
        ("Abdi", "Abdi le somalien souriait."),
        ("Sommalie", "Il partit pour la Sommalie demain."), # Typo
        ("Lhomme", "Lhomme avançait vers lui."), # Glued/Typos
        ("Paris", "Il aime Paris au printemps.")
    ]

    print("\n🔬 DÉBUT DES TESTS NER")
    print("="*60)

    for word, context in test_cases:
        print(f"\n📝 Analyse de '{word}' dans : \"{context}\"")
        result = agent.analyze(word, context)
        
        status = "✅ VALIDE" if result['is_proper_noun'] else "🚫 REJETÉ"
        source = result.get('source', 'Unknown')
        conf = result.get('confidence', 0.0)
        
        print(f"   -> {status} ({source}, Conf={conf:.2f})")
        if 'type' in result:
            print(f"   -> Type: {result['type']}")
        if 'raw' in result:
            print(f"   -> Raw Mistral: {result['raw'][:50]}...")

    print("\n" + "="*60)
    print("Fin des tests.")

if __name__ == "__main__":
    test_ner_agent()
