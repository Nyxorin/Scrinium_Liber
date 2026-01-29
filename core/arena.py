
import random
import os
import sys
import json
import time

try:
    from llama_cpp import Llama
except ImportError:
    print("ERREUR: llama-cpp-python n'est pas installé.")
    sys.exit(1)

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.saboteur import SaboteurAgent # Updated Import
from core.defender_agent import DefenderAgent
from core.antibody_learning import AntibodyLearner
from core.analyst_agent import AnalystAgent

class Arena:
    """
    The GAN Arena (Phase 22 - Updated for Bmad/DrQ Evolution).
    Manages the 'Arms Race' loop between Saboteur and Defender.
    """
    def __init__(self, model_path: str = "models/mistral-7b-instruct-v0.3.Q4_K_M.gguf"):
        self.model_path = model_path
        
        print("\n🏟️ Opening the Arena...")
        # Saboteur is now lightweight (Rule-based Bmad Agent)
        self.saboteur = SaboteurAgent() 
        
        print("🛡️ Connecting to Defender Agent...")
        self.defender = DefenderAgent(model_path)
        self.learner = AntibodyLearner()
        
        print("🔥 Igniting The Analyst (SmartRule Inference)...")
        self.analyst = AnalystAgent()
        self.generated_rules = []
        self.score_defender = 0
        self.score_saboteur = 0
        self.history = []

    def fight_contextual(self, rounds=100):
        """
        [Phase 28/30/32] Real-World Gym Loop.
        1. Saboteur attacks real text (OCR Simulation).
        2. Le Correcteur corrects.
        3. Logic Forge generates code.
        4. Evolution: Saboteur learns from success/failure.
        """
        print(f"\n🏟️ ARENA: CONTEXTUAL DUEL ({rounds} Rounds)")
        print(f"📄 Source: Real Text")
        print(f"🔥 Logic Forge: ACTIVE")
        print(f"🧬 Evolution: ACTIVE (DrQ DNA)")
        
        self.history = []
        
        for r in range(1, rounds + 1):
            print(f"\n🔔 Duel {r}/{rounds}")
            
            # 1. Saboteur Attack (OCR only)
            trap, ground_truth, strategy = self.saboteur.attack()
            
            if trap == "Erreur Corpus":
                print("⚠️ Saboteur missed corpus.")
                continue

            print(f"🦹 Saboteur: ATTACK! Strategy={strategy}")
            # print(f"   Trap: '{trap}'") # Verbose
                 
            # 2. Defense
            print(f"   ► Le Correcteur scanning...")
            defense = self.defender.correct_segment(trap)
            
            # 3. Judgment
            winner = "Draw"
            saboteur_won = False
            
            if defense == ground_truth:
                print("   ✅ Le Correcteur RESTORED Damage.")
                winner = "Correcteur"
                self.score_defender += 1.0
                saboteur_won = False
            elif defense == trap:
                print("   ⚠️ Le Correcteur SKIPPED (Inertia).")
                winner = "Saboteur"
                self.score_saboteur += 1.0
                saboteur_won = True
            else:
                print("   ❓ Le Correcteur FAILED FIX / HALLUCINATED.")
                winner = "Saboteur"
                self.score_saboteur += 3.0
                saboteur_won = True

            # 4. Evolution (The Dream Loop)
            # Saboteur learns immediately
            self.saboteur.learn_from_feedback(strategy, saboteur_won)

            # 5. Phase 35: ANALYST AGENT (Smart Inference)
            if winner == "Correcteur" and trap != ground_truth:
                 print("   🔥 Analyst: Observing Match for Inference...")
                 diffs = self.analyst.analyze_match(trap, ground_truth)
                 if diffs:
                     for rule in diffs:
                         print(f"   📜 SMART RULE INFERRED: {rule}")
                         self.generated_rules.append(rule)
                         with open("data/logic_forge_rules.jsonl", "a") as f:
                             f.write(json.dumps(rule) + "\n")

            # Learning (Antibody) - Legacy
            if winner == "Saboteur":
                 self.learner.learn_from_failures(trap, defense)
                 
            self.history.append({
                "round": r,
                "type": strategy,
                "winner": winner
            })

    def report(self):
        print("\n🏆 MATCH REPORT 🏆")
        print(f"Saboteur: {self.score_saboteur}")
        print(f"Correcteur: {self.score_defender}")
        
        if self.score_defender > self.score_saboteur:
            print("👉 VICTORY: The Immune System is robust.")
        else:
            print("👉 DEFEAT: The Saboteur found cracks in the shield.")
            
        # Save Stats
        try:
             self.defender.save_stats()
             print("✅ Defender Stats Saved.")
        except: pass
        
        try:
            self.saboteur.save_dna()
            print("✅ Saboteur DNA Saved.")
        except: pass

if __name__ == "__main__":
    print("🏟️  REAL-WORLD GYM (CONTEXTUAL - 10 MATCHES) 🏟️")
    arena = Arena()
    for i in range(1, 4):
        print(f"\n🔹 MATCH {i}/3 START (20 Rounds)")
        arena.fight_contextual(20)
        arena.report()
    print("\n🏆 END OF GYM SESSION 🏆")
