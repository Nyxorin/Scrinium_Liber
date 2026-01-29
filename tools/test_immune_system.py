from core.immune_system import ImmuneSystem

def test_immune_system():
    immune = ImmuneSystem()
    
    test_text = "Malko est allé en Sommalie. Il a vu alko boire."
    expected_text = "Malko est allé en Somalie. Il a vu Malko boire."
    
    print("🧪 Starting Immune System Tests...")
    
    result = immune.attack(test_text)
    
    if result == expected_text:
        print(f"✅ Input: '{test_text}'\n   Output: '{result}'")
    else:
        print(f"❌ Input: '{test_text}'\n   Expected: '{expected_text}'\n   Got: '{result}'")

    # Test Learning
    print("\n🧪 Testing Learning Capability...")
    immune.learn_antigen("TestVirus", "TestVaccin")
    res2 = immune.attack("Je suis infecté par TestVirus.")
    if "TestVaccin" in res2:
        print("✅ Learning Successful: TestVirus -> TestVaccin")
    else:
        print(f"❌ Learning Failed. Got: {res2}")

if __name__ == "__main__":
    test_immune_system()
