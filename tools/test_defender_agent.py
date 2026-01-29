import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.defender_agent import DefenderAgent

def test_agent():
    print("🧪 Testing Defender Agent (Phase 29)...")
    
    # 1. Initialize
    agent = DefenderAgent()
    
    # 2. Test Correction
    trap = "L'ho mme marchait."
    print(f"   Input: '{trap}'")
    
    correction = agent.correct_segment(trap)
    print(f"   Output: '{correction}'")
    
    if "L'homme marchait" in correction:
        print("✅ SUCCESS: Correction worked via Daemon.")
    else:
         print(f"❌ FAILURE: Unexpected output '{correction}'")
         
    # 3. Test Crash/Restart (Simulated)
    print("\n💥 Simulating Daemon Crash (Kill)...")
    if agent.daemon_process:
        agent.daemon_process.kill()
        agent.daemon_process.wait()
        
    print("   Sending new request (should auto-restart)...")
    trap2 = "Une mai son rouge."
    correction2 = agent.correct_segment(trap2)
    print(f"   Output 2: '{correction2}'")
    
    if "Une maison rouge" in correction2 or "rouge" in correction2:
        print("✅ SUCCESS: Auto-restart worked.")
    else:
        print(f"❌ FAILURE: Auto-restart failed.")

    agent.close()

if __name__ == "__main__":
    test_agent()
