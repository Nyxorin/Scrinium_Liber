from core.macrophage import Macrophage

def test_macrophage():
    macro = Macrophage()
    
    test_cases = [
        ("lhomme", "l'homme"),
        ("dela", "de la"),      # Might fail if not coded for space split
        ("Lhomme", "L'homme"),  # Capitalized check
        ("MalkoLinge", "Malko Linge"), # CamelCase
        ("pomme", "pomme"),     # Should not change
        ("Sommalie", "Sommalie"), # Should not change (no split makes 2 valid words)
        ("cest", "c'est")
    ]

    print("🧪 Starting Macrophage Tests...")
    for input_word, expected in test_cases:
        result = macro.digest(input_word)
        status = "✅" if result == expected else f"❌ (Got: {result})"
        print(f"Input: {input_word:<15} | Expected: {expected:<15} | {status}")

if __name__ == "__main__":
    test_macrophage()
