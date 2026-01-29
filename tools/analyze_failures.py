
import os
import sys
import json
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.arena import Arena

def analyze_failures(rounds=50):
    print(f"🕵️ Analyzing Defender Failures ({rounds} rounds)...")
    arena = Arena()
    arena.fight(rounds)
    
    failures = {
        "Inertia Broken (Translation/Rewrite)": [],
        "Missed Correction (Blindness)": [],
        "Hallucination (Toxic)": []
    }
    
    print("\n🔍 FAILURE ANALYSIS")
    print("===================")
    
    for event in arena.history:
        if event['winner'] == "Saboteur":
            rule = event['type']
            trap = event['trap']
            defense = event['defense']
            
            # Determine Failure Type
            if rule in ["Semantic Trap (Absurd Logic)", "English Injection (False Friend)", "Pseudo-Typo (Valid Homonym)"]:
                # Expected Inertia -> But changed
                category = "Inertia Broken (Translation/Rewrite)"
            elif rule in ["Visual Trap (Tesseract Noise)", "Logic Trap (Strict Rules)"]:
                # Expected Restoration
                if trap == defense:
                    category = "Missed Correction (Blindness)"
                else:
                    category = "Hallucination (Toxic)"
            else:
                category = "Unknown"
                
            failures[category].append({
                "rule": rule,
                "input": trap,
                "output": defense
            })

    # Report
    for cat, items in failures.items():
        print(f"\n❌ {cat}: {len(items)}")
        if items:
            for item in items[:5]: # Show top 5 examples
                print(f"   - Rule: {item['rule']}")
                print(f"     Qw: '{item['input']}'")
                print(f"     Ax: '{item['output']}'")
                
    total_failures = sum(len(x) for x in failures.values())
    print(f"\nTotal Failures Analyzed: {total_failures}")

if __name__ == "__main__":
    analyze_failures(50)
