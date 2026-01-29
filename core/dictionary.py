#!/usr/bin/env python3
"""
Module de gestion du dictionnaire français enrichi.
Module CORE - Base commune solide (Odoo principle)

Sources:
- Megalex: 336,447 lemmes français
- Lexique.org: 142,694 mots + fréquences (à intégrer)
- Formes conjuguées: À générer
- Contractions: Liste exhaustive
"""
import os
try:
    from spellchecker import SpellChecker
except ImportError:
    print("ERREUR CRITIQUE: pyspellchecker manquant. Install: pip install pyspellchecker")
    SpellChecker = None
    
from typing import List

class FrenchDictionary:
    """
    Gestionnaire universel du dictionnaire français (V5 - Pyspellchecker engine).
    Remplace l'ancienne version statique (Pickle) par un moteur dynamique.
    """

    def __init__(self, megalex_path: str = None):
        # On ignore megalex_path en V5, on utilise le moteur interne
        self.spell = None
        self.whitelist = set()
        if SpellChecker:
            self.spell = SpellChecker(language='fr')
            print("✓ Moteur linguistique chargé: Pyspellchecker (fr)")
        else:
            print("⚠️ Aucun moteur linguistique disponible.")
        
        # Tentative de chargement d'une whitelist globale
        self.load_whitelist("data/knowledge/whitelist.json")

    def load_whitelist(self, path: str):
        """Charge une liste de mots de confiance (noms propres, etc.)"""
        if os.path.exists(path):
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.whitelist.update([w.lower() for w in data])
                        print(f"✅ Whitelist chargée: {len(data)} mots.")
            except Exception as e:
                print(f"⚠️ Erreur chargement whitelist: {e}")

    def validate(self, word: str) -> bool:
        """
        Vérifie si un mot est valide.
        """
        if not self.spell:
            return True # Fail open si pas de dico

        # Nettoyage
        clean_word = word.strip(".,;:?!'\"()[]-")
        if not clean_word:
            return True
            
        # 0. Vérification Whitelist (Prioritaire)
        if clean_word.lower() in self.whitelist:
            return True

        # Pyspellchecker gère tout (pluriels, conjugaisons)
        # Mais attention aux apostrophes (ex: l'arbre)
        
        # Si apostrophe présente, on scande et on vérifie chaque morceau
        if "'" in clean_word:
            parts = clean_word.replace("'", " ").split()
            # On ne vérifie que les parties significatives (>1 lettre) ou connues
            # ex: "l" est ok, "d" est ok.
            unknowns = set()
            for part in parts:
                # On accepte les déterminants élidés standards sans vérifier le dico
                if part.lower() in ['l', 'd', 'n', 'j', 'm', 't', 's', 'c', 'qu']:
                    continue
                # On check aussi la whitelist pour chaque partie
                if part.lower() in self.whitelist:
                    continue
                if len(self.spell.unknown([part])) > 0:
                    unknowns.add(part)
        else:
            unknowns = self.spell.unknown([clean_word])
            
        return len(unknowns) == 0

    def get_similar(self, word: str, n: int = 5) -> List[str]:
        """Trouve les mots similaires/candidats."""
        if not self.spell:
            return []
        return list(self.spell.candidates(word) or [])[:n]

    # --- Méthodes Legacy (Compatibilité V3/V4) ---
    def _load_megalex(self): pass
    def _add_basic_contractions(self): pass
    def add_word(self, word: str, f=0): 
        if self.spell: self.spell.word_frequency.load_words([word])
    def stats(self): return {'engine': 'pyspellchecker', 'status': 'active' if self.spell else 'inactive'}


    # --- Méthodes Legacy Stubbed (Compatibilité) ---
    def get_frequency(self, word: str) -> float:
        return 0.0 # Pas de fréquence dispo immédiatement via API simple

    def add_word(self, word: str, frequency: float = 0.0):
        if self.spell:
             self.spell.word_frequency.load_words([word])

    def add_conjugated_form(self, form: str): pass
    def add_contraction(self, contraction: str): pass
    def load_lexique_org(self, path): pass
    def generate_conjugated_forms(self, verbs): pass

    def print_stats(self):
        print(f"Stats V5: {self.stats()}")

if __name__ == "__main__":
    d = FrenchDictionary()
    d.print_stats()
    print(d.validate("maison"))
