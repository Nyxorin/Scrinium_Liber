#!/usr/bin/env python3
import sys
import os
import json
import traceback

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from correctors.semantic_corrector import SemanticCorrector

def main():
    """
    Defender Daemon (Phase 29).
    Hosts the SemanticCorrector (LLM) in a separate process.
    Communication via Stdin/Stdout (JSON-RPC style).
    """
    # 1. Initialize Model
    # IMPORTANT: Llama.cpp outputs C-level logs to stdout. We MUST capture/redirect them to stderr
    # to protect the JSON communication channel on stdout.
    
    # Save original stdout
    original_stdout_fd = sys.stdout.fileno()
    saved_stdout_fd = os.dup(original_stdout_fd)
    
    try:
        logging_prefix = "[DefenderDaemon]"
        sys.stderr.write(f"{logging_prefix} Initializing SemanticCorrector (Redirecting noise to stderr)...\n")
        
        # Redirect stdout to stderr
        sys.stdout.flush()
        os.dup2(sys.stderr.fileno(), original_stdout_fd)
        
        # We assume standard model path or allow env var override
        model_path = os.environ.get("DEFENDER_MODEL_PATH", "models/mistral-7b-instruct-v0.3.Q4_K_M.gguf")
        corrector = SemanticCorrector(model_path=model_path)
        
        # Restore stdout
        sys.stdout.flush()
        os.dup2(saved_stdout_fd, original_stdout_fd)
        
        # [Handshake] Signal Ready on Stdout
        print(json.dumps({"status": "ready"}), flush=True)
        sys.stderr.write(f"{logging_prefix} Ready. Waiting for requests.\n")
    except Exception as e:
        # Restore stdout just in case
        os.dup2(saved_stdout_fd, original_stdout_fd)
        sys.stderr.write(f"{logging_prefix} CRITICAL INIT ERROR: {e}\n")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        os.close(saved_stdout_fd)


    # 2. Event Loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break # EOF
                
            req = json.loads(line)
            command = req.get("command")
            
            response = {"status": "error", "data": None}
            
            # [Phase 37] Capture logic output to stderr
            # We must NOT let any print() or LLM noise hit stdout during processing
            original_stdout_fd = sys.stdout.fileno()
            saved_stdout_fd = os.dup(original_stdout_fd)
            
            try:
                # Redirect stdout to stderr
                sys.stdout.flush()
                os.dup2(sys.stderr.fileno(), original_stdout_fd)
                
                if command == "ping":
                    response = {"status": "ok", "data": "pong"}
                    
                elif command == "correct_segment":
                    text = req.get("text", "")
                    fever = req.get("fever_mode", False)
                    # Forward to LLM
                    corrected = corrector.correct_segment(text, fever_mode=fever)
                    response = {"status": "ok", "data": corrected}
                    
                elif command == "reload_model":
                     # Optional: Hot reload
                     pass
                elif command == "save_stats":
                     if hasattr(corrector, "rule_applicator") and corrector.rule_applicator:
                         corrector.rule_applicator.save_stats()
                     response = {"status": "ok"}
                     
            finally:
                # Restore stdout for the JSON response
                sys.stdout.flush()
                os.dup2(saved_stdout_fd, original_stdout_fd)
                os.close(saved_stdout_fd)

            # Send Response (Now stdout is restored)
            print(json.dumps(response), flush=True)
            
        except BrokenPipeError:
             sys.exit(0)
        except json.JSONDecodeError:
            sys.stderr.write(f"{logging_prefix} Invalid JSON received.\n")
        except Exception as e:
            sys.stderr.write(f"{logging_prefix} ERROR processing request: {e}\n")
            try:
                print(json.dumps({"status": "error", "error": str(e)}), flush=True)
            except:
                pass
                
if __name__ == "__main__":
    # Ignore SIGPIPE to prevent crash on print if parent closes
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
