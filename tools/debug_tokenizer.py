import sys
import os

print("1. Setup Environment...")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

print("2. Import Transformers (No Backend)...")
from transformers import AutoTokenizer

print("3. Load CamemBERT Tokenizer (Slow)...")
try:
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner", use_fast=False)
    print("   Tokenizer Loaded.")
except Exception as e:
    print(f"   FATAL: Tokenizer failed: {e}")
    sys.exit(1)

print("4. Tokenize Test...")
try:
    tokens = tokenizer.tokenize("Malko")
    print(f"   Tokens: {tokens}")
except Exception as e:
    print(f"   FATAL: Tokenization failed: {e}")
    sys.exit(1)

print("✅ SUCCESS.")
