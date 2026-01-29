import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.smart_rule_applicator import SmartRuleApplicator
from core.rule_optimizer import RuleOptimizer

def test_simulation():
    print("🚦 TESTING AUTOROUTE SYSTEM...")
    
    # 1. Create a temporary rule file
    test_rules_path = "data/test_rules.jsonl"
    with open(test_rules_path, "w") as f:
        f.write(json.dumps({"trigger_word": "autoroute", "correction": "highway", "conditions": [], "usage_count": 0}) + "\n")
        f.write(json.dumps({"trigger_word": "chemin", "correction": "path", "conditions": [], "usage_count": 0}) + "\n")
    
    # 2. Convert Applicator to use this file
    app = SmartRuleApplicator(rules_path=test_rules_path)
    
    # 3. Apply "autoroute" rule 5 times, "chemin" 1 time
    text_autoroute = "Je prends l'autoroute."
    text_chemin = "Je prends le chemin."
    
    print("   Running applications...")
    for _ in range(5):
        app.apply_rules(text_autoroute)
        
    app.apply_rules(text_chemin)
    
    # 4. Trigger Save
    print("   Saving stats...")
    app.save_stats()
    
    # 5. Verify order
    print("   Verifying storage order (Hot Path)...")
    with open(test_rules_path, "r") as f:
        lines = f.readlines()
        rule1 = json.loads(lines[0])
        rule2 = json.loads(lines[1])
        
        print(f"   Position 1: {rule1['trigger_word']} (Count: {rule1['usage_count']})")
        print(f"   Position 2: {rule2['trigger_word']} (Count: {rule2['usage_count']})")
        
        if rule1['trigger_word'] == "autoroute" and rule1['usage_count'] == 5:
            print("✅ SUCCESS: 'autoroute' is #1 with 5 hits.")
        else:
            print("❌ FAILURE: Sorting or counting incorrect.")

    # Cleanup
    os.remove(test_rules_path)

if __name__ == "__main__":
    test_simulation()
