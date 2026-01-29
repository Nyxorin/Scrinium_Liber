import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.rule_optimizer import RuleOptimizer

def migrate():
    print("🚀 Starting Migration: Adding 'usage_count' to all rules...")
    optimizer = RuleOptimizer()
    
    # Just loading and saving triggers the default value logic in RuleOptimizer._load_rules
    # and saving writes the new schema.
    optimizer.optimize_storage()
    
    print("✅ Migration Complete.")

if __name__ == "__main__":
    migrate()
