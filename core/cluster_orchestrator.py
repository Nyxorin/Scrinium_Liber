
import threading
import queue
import time
import math
import sys
import os
from typing import List, Tuple

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.defender_agent import DefenderAgent

class ClusterFactory:
    """
    Phase 31: The Factory.
    Orchestrates multiple DefenderAgents in parallel to process a book.
    Architecture:
    - Slicer: Splits text into chunks.
    - Worker Pool: N concurrent DefenderAgents (using Threading, as they wait on IO).
    - Assembler: Merges results in order.
    """
    def __init__(self, model_path: str = "models/mistral-7b-instruct-v0.3.Q4_K_M.gguf", num_workers: int = 2):
        self.model_path = model_path
        self.num_workers = num_workers
        self.agents = []
        self.is_running = False

    def start_factory(self):
        """
        Initializes the fleet of Agents.
        """
        print(f"🏭 CLUSTER FACTORY STARTING ({self.num_workers} Workers)...")
        for i in range(self.num_workers):
            print(f"   🔧 Spawning Worker #{i+1}...")
            agent = DefenderAgent(self.model_path)
            self.agents.append(agent)
            time.sleep(1) # Stagger start to avoid disk/cpu spike
        self.is_running = True
        print("✅ FACTORY OPERATIONAL.")

    def shutdown_factory(self):
        """
        Shuts down all agents.
        """
        print("🏭 FACTORY SHUTDOWN initiated...")
        for i, agent in enumerate(self.agents):
            print(f"   💤 Stopping Worker #{i+1}...")
            agent.stop()
        self.is_running = False
        print("✅ FACTORY OFFLINE.")

    def _worker_task(self, agent: DefenderAgent, task_queue: queue.Queue, results: dict, worker_id: int):
        """
        Thread loop for a single worker.
        """
        while True:
            try:
                # Non-blocking get to allow periodic check
                chunk_index, chunk_text = task_queue.get(timeout=1)
            except queue.Empty:
                if not self.is_running: # Should we stop?
                    break
                # If running but empty, just break (work done)
                # But we usually fill queue before starting threads
                continue

            if chunk_text is None: # Sentinel
                break

            print(f"   🔨 Worker #{worker_id} processing Chunk #{chunk_index} ({len(chunk_text)} lines)...")
            
            # Process lines
            corrected_lines = []
            for line in chunk_text:
                if not line.strip():
                    corrected_lines.append(line)
                    continue
                
                # Call the Agent
                # Retry logic is handled inside DefenderAgent for Daemon crashes
                # But here we assume Agent is robust.
                correction = agent.correct_segment(line.strip())
                corrected_lines.append(correction + "\n") # Restore newline? (simplified)
            
            results[chunk_index] = "".join(corrected_lines)
            task_queue.task_done()
            print(f"   ✅ Worker #{worker_id} finished Chunk #{chunk_index}.")

    def process_text(self, full_text: str) -> str:
        """
        Main entry point.
        1. Slice text.
        2. Distribute to workers.
        3. Collect and merge.
        """
        if not self.agents:
            raise RuntimeError("Factory not started! Call start_factory() first.")

        lines = full_text.splitlines(keepends=True)
        total_lines = len(lines)
        if total_lines == 0:
            return ""

        # Logic: Split into N chunks? Or smaller micro-chunks?
        # Smaller chunks balances load better (if one chunk is hard).
        # Let's say we want ~30 lines per chunk for granulrity? Or bigger?
        # Agent overhead is small (process is persistent).
        # Let's target K chunks where K = Workers * 4 (Load balancing)
        
        chunk_size = math.ceil(total_lines / (self.num_workers * 4))
        if chunk_size < 10: chunk_size = 10 # Minimum size
        
        chunks = []
        for i in range(0, total_lines, chunk_size):
            chunks.append((i // chunk_size, lines[i:i + chunk_size]))
            
        print(f"📦 JIT SLICER: Split {total_lines} lines into {len(chunks)} Jobs (Size ~{chunk_size}).")
        
        # Setup Queue
        task_queue = queue.Queue()
        for c in chunks:
            task_queue.put(c)
            
        # Results storage (Thread-safe dict)
        results = {}
        
        # Launch Threads
        threads = []
        for i, agent in enumerate(self.agents):
            t = threading.Thread(target=self._worker_task, args=(agent, task_queue, results, i+1))
            t.start()
            threads.append(t)
            
        # Wait for Queue to be empty
        task_queue.join()
        
        # Signal threads to stop? (They are stuck in get maybe if not carefully managed)
        # Actually task_queue.join() blocks until all tasks done.
        # But threads are still looping.
        # We need to signal them.
        self.is_running = False # This might be loose
        # Or sentinel
        # But we reused the queue logic above
        
        # Let's join threads (they check self.is_running or empty)
        # My _worker_task Loop has 'if queue.Empty... break' logic logic needs refinement
        # If queue empty AND work done -> break.
        # task_queue.join() only returns when count is 0.
        
        # Merging
        print("🔗 ASSEMBLER: Merging results...")
        final_output = []
        # Sort by chunk index
        sorted_indices = sorted(results.keys())
        for idx in sorted_indices:
            final_output.append(results[idx])
            
        return "".join(final_output)

if __name__ == "__main__":
    # Test
    print("🧪 TEST MODE: ClusterFactory")
    # Fake text
    text = "L'homme marchait.\nIl vit une bicoque.\nC'était bien.\n" * 20
    
    factory = ClusterFactory(num_workers=1)
    try:
        factory.start_factory()
        result = factory.process_text(text)
        print("\n📝 RESULT HEAD:")
        print(result[:100])
    finally:
        factory.shutdown_factory()
