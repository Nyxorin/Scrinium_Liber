import json
import os
import logging

class RuleOptimizer:
    """
    The 'Autoroute' System.
    Optimizes the rule database by sorting frequently used rules to the top (Hot Path).
    """

    def __init__(self, rules_path: str = "data/logic_forge_rules.jsonl"):
        self.rules_path = rules_path
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        """Loads rules from JSONL file."""
        if not os.path.exists(self.rules_path):
            logging.warning(f"Rule file not found: {self.rules_path}")
            return

        with open(self.rules_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        rule = json.loads(line)
                        # Ensure usage_count exists
                        if "usage_count" not in rule:
                            rule["usage_count"] = 0
                        self.rules.append(rule)
                    except json.JSONDecodeError:
                        continue
        
        logging.info(f"RuleOptimizer loaded {len(self.rules)} rules.")

    def increment_usage(self, trigger_word: str):
        """
        Increments usage count for a rule matching the trigger word.
        Note: Ideally rules should have unique IDs. For now, we use trigger_word.
        """
        found = False
        for rule in self.rules:
            # Match by trigger_word if available (SmartRule)
            if rule.get("trigger_word") == trigger_word:
                rule["usage_count"] += 1
                found = True
                # Break? Or continue in case of duplicates? 
                # Let's break for efficiency, assuming uniqueness logic elsewhere.
                break 
            
            # Fallback for simple Regex Replacement rules (no trigger_word)
            # We assume "pattern" is the unique key there
            if "pattern" in rule and not rule.get("type", "") == "SmartRule":
                # Matches by pattern? Hard to know exactly which one triggered without ID.
                # For now, we support SmartRules primarily.
                pass

        return found

    def optimize_storage(self):
        """
        Sorts rules by 'usage_count' (Descending) and saves to disk.
        The 'Autoroute': Top of the file = Most used.
        """
        # Sort: High usage first
        self.rules.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        
        # Save atomicaly (write to temp then rename)
        temp_path = self.rules_path + ".tmp"
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                for rule in self.rules:
                    f.write(json.dumps(rule) + "\n")
            
            os.replace(temp_path, self.rules_path)
            logging.info("Rule database optimized (Autoroute Updated).")
            print(f"🛣️ Autoroute Updated: Rules resorted by frequency.")
        except Exception as e:
            logging.error(f"Failed to optimize rules: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    # Test Run
    opt = RuleOptimizer()
    print("Simulating usage...")
    opt.increment_usage("1'homme") # Example trigger
    opt.optimize_storage()
