
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.arena import Arena

def run_training():
    print("🏟️ Initializing Arena for TRAINING SESSION (10 Matches x 100 Rounds)...")
    try:
        # Init ONCE to save loading time
        arena = Arena()
        
        for i in range(1, 11):
            print(f"\n🔹 MATCH {i}/10 STARTING...")
            arena.fight_contextual(rounds=100)
            arena.report()
            
        print("\n🏆 TRAINING SESSION COMPLETED.")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_training()
