import sys
import json
import os

# Configuration pour isolation totale
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

# Debugging: Log daemon activity to file
import logging
logging.basicConfig(filename='ner_daemon.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
sys.stderr = open('ner_daemon.err', 'w') 

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch

def run_daemon():
    # Configuration conservatrice
    # IMPORTANT: Dans le venv .ner_env, on utilise PyTorch pur.
    torch.set_num_threads(1)
    
    # Chargement du modèle
    try:
        logging.info("Loading Tokenizer (use_fast=False)...")
        # Bug fix: use_fast=False est essentiel sur Mac pour éviter le crash Rust
        tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner", use_fast=False)
        
        logging.info("Loading Model (PyTorch)...")
        model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
        
        logging.info("Creating Pipeline (PyTorch)...")
        nlp = pipeline(
            "ner", 
            model=model, 
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=-1 # CPU forcé
        )
        logging.info("Model loaded successfully (PyTorch).")
    except Exception as e:
        logging.error("Fatal error loading model: %s", e)
        sys.exit(1)

    # Boucle d'écoute
    while True:
        try:
            # Lecture de l'entrée (une ligne JSON = une requête)
            line = sys.stdin.readline()
            if not line:
                break
            
            data = json.loads(line)
            text = data.get("text", "")
            
            # Inférence
            entities = nlp(text)
            
            # Conversion en format sérialisable
            serializable_entities = []
            for ent in entities:
                serializable_entities.append({
                    "word": ent["word"],
                    "entity_group": ent["entity_group"],
                    "score": float(ent["score"]),
                    "start": ent["start"],
                    "end": ent["end"]
                })
            
            # Réponse
            print(json.dumps({"status": "ok", "entities": serializable_entities}))
            sys.stdout.flush()
            
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    run_daemon()
