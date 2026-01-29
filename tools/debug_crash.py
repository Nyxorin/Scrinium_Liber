import sys
import os

print("1. Setup Environment...")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" # Reduce TF spam

print("2. Import TensorFlow...")
import tensorflow as tf
print(f"   TF Version: {tf.__version__}")

print("3. Import Transformers...")
from transformers import AutoTokenizer, TFAutoModelForTokenClassification

print("4. Load Tokenizer (Slow)...")
try:
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner", use_fast=False)
    print("   Tokenizer Loaded.")
except Exception as e:
    print(f"   FATAL: Tokenizer failed: {e}")
    sys.exit(1)

print("5. Load Model (TF)...")
try:
    # from_pt=True allows loading the PyTorch weights into TF model on the fly
    model = TFAutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner", from_pt=True)
    print("   Model Loaded.")
except Exception as e:
    print(f"   FATAL: Model failed: {e}")
    sys.exit(1)

print("6. Inference Test...")
try:
    inputs = tokenizer("Malko", return_tensors="tf")
    outputs = model(inputs)
    print("   Inference Success.")
except Exception as e:
    print(f"   FATAL: Inference failed: {e}")
    sys.exit(1)

print("✅ SUCCESS.")
