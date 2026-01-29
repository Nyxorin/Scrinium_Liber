
import sys
import os
import time
import json
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.arena import Arena

def run_intensive_session(num_matches=50, rounds_per_match=100):
    start_time = datetime.datetime.now()
    log_dir = os.path.join("data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    session_id = start_time.strftime("%Y%m%d_%H%M%S")
    session_log = os.path.join(log_dir, f"intensive_{session_id}.log")
    
    print(f"🚀 INTENSIVE TRAINING SESSION STARTED: {start_time}")
    print(f"📊 Plan: {num_matches} Matches x {rounds_per_match} Rounds (~{num_matches * rounds_per_match} total)")
    print(f"📝 Logging to: {session_log}")
    
    try:
        # Initialize Arena once
        arena = Arena()
        
        for m in range(1, num_matches + 1):
            m_start = datetime.datetime.now()
            print(f"\n──────────────────────────────────────────────────")
            print(f"🔹 MATCH {m}/{num_matches} STARTING at {m_start.strftime('%H:%M:%S')}")
            print(f"──────────────────────────────────────────────────")
            
            try:
                arena.fight_contextual(rounds=rounds_per_match)
                arena.report()
                
                # Snapshot of rules count
                rule_count = 0
                if os.path.exists("data/logic_forge_rules.jsonl"):
                    with open("data/logic_forge_rules.jsonl", "r") as f:
                        rule_count = sum(1 for _ in f)
                
                print(f"📈 Match {m} Complete. Total Rules in Forge: {rule_count}")
                
            except Exception as e:
                print(f"⚠️ Warning: Match {m} interrupted by error: {e}")
                print("🔄 Attempting to recover and continue the session...")
                time.sleep(5) # Cooldown
                continue
                
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        print(f"\n🏆 INTENSIVE SESSION COMPLETED at {end_time}")
        print(f"⏱️ Total Duration: {duration}")
        
    except Exception as e:
        print(f"❌ Critical Error in Session: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Super-Session settings (approx 8 hours)
    # 200 matches ~ 13h -> 120 matches ~ 8h
    run_intensive_session(num_matches=120, rounds_per_match=100)
