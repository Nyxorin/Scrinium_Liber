import sys
import json
import os
import math

# Strict Isolation Configuration
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

# Debugging
import logging
logging.basicConfig(filename='phantom_daemon.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
sys.stderr = open('phantom_daemon.err', 'w') 

from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch

def score_sentence(model, tokenizer, sentence):
    """
    Calculates the Pseudo-Perplexity (PPL) of a sentence using CamemBERT MLM.
    Method: Iterative Masking (Pseudo-Log-Likelihood Scores).
    We mask each token one by one and sum the cross-entropy loss.
    This prevents the model from "seeing the answer" (Self-Prediction Cheating).
    """
    inputs = tokenizer(sentence, return_tensors='pt')
    input_ids = inputs["input_ids"] # Shape [1, seq_len]
    attention_mask = inputs["attention_mask"]
    
    seq_len = input_ids.shape[1]
    total_loss = 0
    num_tokens = 0
    
    # 0 = CLS, -1 = SEP. We only score the "content" tokens.
    # Note: If sentence is empty or just special tokens, return 0.
    if seq_len <= 2:
        return 0.0

    # Create a batch of masked inputs for speed?
    # For now, simplistic iterative loop (safer context)
    
    # Original tensor must be cloned to avoid modifying it in place permanently
    # But we can modify and restore.
    
    token_ids = input_ids[0].clone()
    
    for i in range(1, seq_len - 1): # Skip CLS (0) and SEP (last)
        original_id = token_ids[i].item()
        
        # Mask this token
        token_ids[i] = tokenizer.mask_token_id
        
        # Forward pass (Batch size 1)
        with torch.no_grad():
            outputs = model(token_ids.unsqueeze(0), attention_mask=attention_mask)
            
        # Get logits for the masked position
        logits = outputs.logits[0, i] # Shape [vocab_size]
        
        # Calculate CrossEntropyLoss for this token
        # Expected shape for CrossEntropy: Input (N, C), Target (N)
        # Here: Input (1, Vocab), Target (1)
        loss = torch.nn.functional.cross_entropy(logits.view(1, -1), torch.tensor([original_id]))
        
        total_loss += loss.item()
        num_tokens += 1
        
        # Restore original token for next iteration
        token_ids[i] = original_id
        
    if num_tokens == 0:
        return 0.0
        
    return math.exp(total_loss / num_tokens)

def run_daemon():
    # Use pure PyTorch config
    torch.set_num_threads(1)
    
    try:
        logging.info("👻 Phantom Protocol: Loading Tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("camembert-base", use_fast=False)
        
        logging.info("👻 Phantom Protocol: Loading Model (MaskedLM)...")
        model = AutoModelForMaskedLM.from_pretrained("camembert-base")
        model.eval() # Set to evaluation mode
        
        logging.info("✅ Phantom Ready.")
    except Exception as e:
        logging.error("Fatal error loading Phantom: %s", e)
        sys.exit(1)

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            data = json.loads(line)
            sentence = data.get("text", "")
            
            # Calculate Perplexity
            ppl = score_sentence(model, tokenizer, sentence)
            
            response = {
                "status": "ok",
                "perplexity": ppl,
                "verdict": "FLUID" if ppl < 30 else "WEIRD"
            }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
            logging.info(f"Scored '{sentence[:20]}...': {ppl:.2f}")

        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    run_daemon()
