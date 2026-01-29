import re
from typing import Optional, Dict
from correctors.semantic_corrector import SemanticCorrector

class Grammarian:
    """
    Agent spécialisé dans l'analyse grammaticale pour identifier les Noms Propres.
    Il utilise le LLM pour déterminer si un mot inconnu joue un rôle de Nom Propre
    (Sujet, Complément de nom, etc.) ou s'il s'agit d'une erreur.
    """

    def __init__(self, semantic_corrector: Optional[SemanticCorrector] = None):
        self.semantic = semantic_corrector or SemanticCorrector()
        self.cache = {} # Cache local pour éviter de redemander le même mot dans le même chapitre

    def analyze_word(self, word: str, context: str) -> Dict:
        """
        Analyse le rôle d'un mot dans son contexte.
        Retourne un dictionnaire avec 'is_proper_noun' (bool) et 'reason' (str).
        """
        # Nettoyage de base
        clean_word = word.strip(".,;:?!'\"()[]-")
        
        # Vérification cache
        if clean_word in self.cache:
            return self.cache[clean_word]

        # Si le mot n'a pas de majuscule, c'est rarement un nom propre (en français)
        # Sauf cas particulier, mais on veut être conservateur.
        if not any(c.isupper() for c in clean_word):
             return {"is_proper_noun": False, "role": "unknown", "reason": "No capitalization"}

        # Construction du prompt pour l'analyse grammaticale
        prompt = self._build_grammar_prompt(clean_word, context)
        
        # Appel au LLM via SemanticCorrector
        try:
            # On utilise une température très basse pour une analyse "froide"
            # On demande un format JSON-like ou un tag clair
            response = self.semantic._model(
                prompt,
                max_tokens=100,
                stop=["\n", "[/INST]"],
                temperature=0.0,
                echo=False
            )['choices'][0]['text'].strip()

            analysis = self._parse_llm_response(response)
            self.cache[clean_word] = analysis
            return analysis

        except Exception as e:
            print(f"⚠️ Erreur analyse grammairienne : {e}")
            return {"is_proper_noun": False, "role": "error", "reason": str(e)}

    def _build_grammar_prompt(self, word: str, context: str) -> str:
        """Construit le prompt d'analyse syntaxique."""
        return f"""[INST] Tu es un expert en grammaire française.
Tâche : Analyser la fonction grammaticale du mot "{word}" dans la phrase suivante.

Phrase : "{context}"

Réponds uniquement sous ce format :
ROLE: [Sujet / Objet / Lieu / Temps / Erreur OCR]
NOM_PROPRE: [OUI / NON]
JUSTIFICATION: [Brève explication]

Exemple : 
Phrase : "Malko regarda Abdi."
Mot : "Abdi"
ROLE: Objet
NOM_PROPRE: OUI
JUSTIFICATION: Abdi est un prénom somalien, ici complément d'objet direct.

Mot à analyser : "{word}"
[/INST]"""

    def _parse_llm_response(self, response: str) -> Dict:
        """Extrait les informations du texte généré par le LLM."""
        is_proper = "NOM_PROPRE: OUI" in response.upper()
        role_match = re.search(r"ROLE:\s*(.*)", response, re.IGNORECASE)
        role = role_match.group(1).strip() if role_match else "unknown"
        
        return {
            "is_proper_noun": is_proper,
            "role": role,
            "raw_response": response
        }
