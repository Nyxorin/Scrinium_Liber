
import os
import sys
import difflib
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from correctors.semantic_corrector import SemanticCorrector
from core.dictionary import FrenchDictionary

def benchmark(clean_path, dirty_path, limit=100):
    print(f"run_benchmark: {dirty_path} -> ?")
    
    with open(clean_path, 'r', encoding='utf-8') as f:
        clean_lines = f.readlines()
        
    with open(dirty_path, 'r', encoding='utf-8') as f:
        dirty_lines = f.readlines()
        
    corrector = SemanticCorrector()
    dictionary = FrenchDictionary()
    
    total_lines = 0
    total_errors_in_input = 0
    total_corrections_made = 0
    total_restorations = 0
    total_hallucinations = 0
    total_missed = 0
    
    start_time = time.time()
    
    print("\n🔍 STARTING BENCHMARK...")
    print(f"Target: First {limit} lines with errors.")
    
    for i, (clean, dirty) in enumerate(zip(clean_lines, dirty_lines)):
        clean = clean.strip()
        dirty = dirty.strip()
        
        if not dirty or len(dirty) < 5: continue
        if clean == dirty: continue # Skip lines that were not sabotaged
        
        # We only benchmark sabotaged lines to save time
        total_lines += 1
        total_errors_in_input += 1
        
        # Run Correction
        # Note: We are simulating the "Semantic" step only.
        # In full pipeline, DeterministicCorrector runs first.
        corrected = corrector.correct_segment(dirty)
        
        # Analyze Result
        if corrected == dirty:
            # No change
            if clean == dirty:
                # Correctly did nothing (but we skipped those above)
                pass 
            else:
                 # Missed error
                 total_missed += 1
                 # print(f"❌ MISSED: '{dirty}' (Expected: '{clean}')")
        else:
            total_corrections_made += 1
            if corrected == clean:
                total_restorations += 1
                print(f"✅ RESTORED: '{dirty}' -> '{corrected}'")
            else:
                # Partial fix or hallucination?
                # Calculate improvement
                sim_dirty = difflib.SequenceMatcher(None, dirty, clean).ratio()
                sim_corr = difflib.SequenceMatcher(None, corrected, clean).ratio()
                
                if sim_corr > sim_dirty:
                    # Improvement
                    total_restorations += 0.5 # Partial credit
                    print(f"⚠️ PARTIAL: '{dirty}' -> '{corrected}' (Target: '{clean}')")
                else:
                    total_hallucinations += 1
                    print(f"💀 HALLUCINATION: '{dirty}' -> '{corrected}' (Target: '{clean}')")

        if total_lines >= limit:
            break
            
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n📊 BENCHMARK REPORT")
    print("====================")
    print(f"Lines Processed: {total_lines}")
    print(f"Time Taken: {duration:.2f}s ({duration/total_lines:.2f}s/line)")
    print(f"Errors in Input: {total_errors_in_input}")
    print(f"Corrections Attempted: {total_corrections_made}")
    print(f"SUCCESS (Restorations): {total_restorations} ({total_restorations/total_lines*100:.1f}%)")
    print(f"FAILURES (Missed): {total_missed} ({total_missed/total_lines*100:.1f}%)")
    print(f"HALLUCINATIONS (Worsened): {total_hallucinations} ({total_hallucinations/total_lines*100:.1f}%)")

if __name__ == "__main__":
    benchmark("SAS_006_CLEAN.txt", "SAS_006_SABOTAGED.txt", limit=100)
