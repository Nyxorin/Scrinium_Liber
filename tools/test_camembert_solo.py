import os
# Disable parallelism to be safe
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from transformers import pipeline

def test_camembert():
    print("🏗️ Chargement de CamemBERT NER (Jean-Baptiste/camembert-ner)...")
    try:
        # On force le CPU et le tokenizer lent (Python) pour éviter le crash Rust/Mutex
        print("🔧 Tentative avec use_fast=False...")
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        
        tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner", use_fast=False)
        model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
        
        nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=-1)
        print("✅ Modèle chargé (Slow Tokenizer).")
        
        text = "Malko Linge a rencontré Abdi en Somalie près du Jubba."
        print(f"📝 Analyse de : '{text}'")
        
        results = nlp(text)
        print("🔍 Résultats :")
        for ent in results:
            print(f"   - {ent['entity_group']}: {ent['word']} (Score: {ent['score']:.2f})")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    test_camembert()
