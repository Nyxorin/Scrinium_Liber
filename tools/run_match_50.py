
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.arena import Arena

def run_match():
    print("🏟️ Initializing Arena for 50-Round Contextual Match...")
    # Initialize Arena
    try:
        arena = Arena()
        # Run 50 rounds
        arena.fight_contextual(rounds=50)
        # Show final report
        arena.report()
    except Exception as e:
        print(f"❌ Error during match: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_match()
