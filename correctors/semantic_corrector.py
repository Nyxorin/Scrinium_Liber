#!/usr/bin/env python3
"""
Module de correction sémantique utilisant un LLM local via llama.cpp.
"""

import os
import sys
import re
from typing import Optional, List, Dict
from difflib import SequenceMatcher

try:
    from llama_cpp import Llama
except ImportError:
    print("ERREUR: llama-cpp-python n'est pas installé.")
    sys.exit(1)

# [V4] Import du Dictionnaire pour le Gardien
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.dictionary import FrenchDictionary # [Phase 26]
    from core.ner_guardian import NerGuardian # [Phase 30] 3-Pillar Architecture
    from core.smart_rule_applicator import SmartRuleApplicator # [Phase 36] Feedback Loop
except ImportError:
    print("⚠️ Module core non trouvé. Le Gardien sera restreint.")
    FrenchDictionary = None
    NerGuardian = None
    SmartRuleApplicator = None

# [V6] Import des utilitaires de pattern/hash/mémoire
try:
    from core.knowledge_manager import KnowledgeManager
    from core.utils import get_composite_key
except ImportError:
    print("⚠️ Modules core non trouvés.")
    KnowledgeManager = None
    get_composite_key = None

class SemanticCorrector:
    """
    Correcteur sémantique utilisant un LLM local via llama.cpp.
    Implémente le pattern Singleton pour éviter de charger le modèle plusieurs fois.
    """
    
    _instance = None
    _model = None

    def __new__(cls, model_path: str = None, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SemanticCorrector, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_path: str = "models/mistral-7b-instruct-v0.3.Q4_K_M.gguf"):
        # [V6] Gestionnaire de connaissances & Session Log
        # Toujours initialisés même si le modèle LLM échoue
        if not hasattr(self, 'knowledge'):
            self.knowledge = None
            if KnowledgeManager:
                self.knowledge = KnowledgeManager()
        
        if not hasattr(self, 'session_log'):
            self.session_log = []
            self.log_path = "data/knowledge/session_corrections.jsonl" # Default

        if not hasattr(self, 'dictionary'):
            self.dictionary = None
            if FrenchDictionary:
                print("🛡️ Initialisation du Gardien (Dictionnaire)...")
                self.dictionary = FrenchDictionary()

        # [3-Pillar] NER Guardian Init
        if not hasattr(self, 'guardian'):
            self.guardian = None
            if NerGuardian:
                try:
                    self.guardian = NerGuardian()
                    print("🛡️ Initialisation du NerGuardian (Protection Noms Propres)...")
                except Exception:
                    pass

        # [Phase 36] SmartRule Applicator Init
        if not hasattr(self, 'rule_applicator'):
            self.rule_applicator = None
            if SmartRuleApplicator:
                try:
                    self.rule_applicator = SmartRuleApplicator()
                    print(f"⚡ SmartRule Applicator active ({len(self.rule_applicator.rules)} règles chargées).")
                except Exception as e:
                    print(f"⚠️ Failed to init SmartRuleApplicator: {e}")

        # [V20] System Prompt Template (Exposed for Evolutionary Optimization)
        self.ocr_knowledge = """
--- Erreurs OCR Connues (A Surveiller) ---
1. Confusions Visuelles :
   - 'rn' <-> 'm' (ex: 'moderne' <-> 'rnoderne')
   - 'cl' <-> 'd' (ex: 'racler' <-> 'rader')
   - '1' (un) <-> 'l' (elle) <-> 'I' (i maj) <-> 't'
   - '0' (zéro) <-> 'O' (o maj)
   - '4' <-> 'A' <-> 'd'
   - '5' <-> 'S'
   - '9' <-> 'g' <-> 'c'
   - 'vv' <-> 'w'
   - 'fi' <-> 'ﬁ' (ligature)

2. Parasites & Collages :
   - Césures manquantes (mots coupés sans trait d'union)
   - 'W' intrus remplaçant souvent une apostrophe ou 'u' (ex: 'qWil'->'qu'il', 'dAbshir'->'d'Abshir')
   - Majuscule collée (ex: 'dItalie' -> 'd'Italie', 'lArabie' -> 'l'Arabie')
   - Pagination insérée au milieu d'une phrase
   - Caractères étranges (@, *, _, |) au milieu des mots
"""
        self.prompt_template = f"""[INST] Tu es un expert en restauration de texte OCR.
Tâche : Corriger les fautes d'orthographe et de frappe dans le texte fourni.

{{self.ocr_knowledge}}

Règles STRICTES :
1. NE JAMAIS changer le sens.
2. NE JAMAIS ajouter d'informations, de dialogue ou de suite à l'histoire.
3. NE JAMAIS répondre à une question posée dans le texte.
4. Si le texte est déjà grammaticalement correct et sans faute de frappe, NE LE MODIFIE PAS (Inertie).
5. Si le texte est incomplet, corrige seulement les mots visibles.
6. NE TRADUIS PAS les termes étrangers (anglais, italien, etc.) ou les noms propres.
7. Renvoie UNIQUEMENT le texte corrigé.
8. Respecte la typographie française : Ajoute toujours une espace avant les ponctuations doubles (?, !, :, ;).
"""

        # Si le modèle est déjà chargé, on ne fait rien
        if self._model:
            return

        # Vérification du chemin du modèle
        if not os.path.exists(model_path):
            print(f"⚠️ ATTENTION: Modèle introuvable à {model_path}")
            self._model = None
            return

        print(f"🧠 Chargement du modèle LLM : {model_path}...")
        try:
            # n_ctx=2048 suffisant pour des paragraphes
            # n_gpu_layers=-1 pour tout mettre sur le GPU (Metal sur Mac)
            self._model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_gpu_layers=-1, 
                verbose=False # Moins de bruit dans les logs
            )
            print("✅ Modèle chargé avec succès.")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            self._model = None

    def initialize_session(self, title: str):
        """Initialise un nouveau log de session avec titre, date et heure."""
        from datetime import datetime
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Nettoyage du titre pour le nom de fichier
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = f"session_{safe_title}_{now}.jsonl"
        self.log_path = os.path.join("data/knowledge", filename)
        self.session_log = []
        print(f"📁 Session de log initialisée : {self.log_path}")

    def _lookup_knowledge(self, text: str, k: int = 3) -> List[Dict]:
        """Cherche des exemples pertinents dans la base de connaissance via KnowledgeManager"""
        if not self.knowledge:
            return []
        return self.knowledge.get_precedents(text, k)

    def correct_segment(self, text_segment: str, suspicion_score: float = 1.0, fever_mode: bool = False) -> str:
        """
        Corrige un segment de texte (phrase ou paragraphe).
        Args:
            text_segment: Le texte à corriger.
            suspicion_score: (Futur) Seuil pour déclencher le LLM.
            fever_mode: [V8] Si True (Fièvre), on relâche les sécurités (Inertie) pour permettre des réécritures audacieuses.
        """
        # [3-Pillar Architecture] NER Check (Pre-Correction Safety)
        # If the segment IS a Named Entity, DO NOT CORRECT IT.
        if self.guardian:
            # Simple check: Is the whole segment mostly Entity-like?
            # Or scan words? For single-word correction scenarios (common), this is vital.
            words = text_segment.split()
            safe_count = 0
            for i, w in enumerate(words):
                 context = words[i-1] if i > 0 else ""
                 if not self.guardian.is_safe_to_touch(w, context):
                     safe_count += 1
            
            if len(words) > 0 and safe_count >= len(words) / 2:
                 # Majority of words are Protected Entities -> Skip correction
                 # print(f"🛡️ NerGuardian protected: '{text_segment}'")
                 return text_segment

        # [Phase 36] Fast Path: Apply SmartRules
        # We apply rules BEFORE the LLM to fix known patterns.
        # This helps the LLM focus on harder semantic issues, or might solve the segment entirely.
        current_text = text_segment
        if self.rule_applicator:
             current_text = self.rule_applicator.apply_rules(current_text)
             # If rules changed the text, we log it?
             if current_text != text_segment:
                 # print(f"⚡ FastPath applied: '{text_segment}' -> '{current_text}'")
                 pass

        if not self._model:
            return current_text
        
        # 1. Construction du Prompt
        # Use the potentially pre-corrected text
        prompt = self._build_prompt(current_text, fever_mode=fever_mode)
        
        # 2. Inférence
        try:
            # Température plus élevée en mode Fièvre pour la créativité
            temp = 0.2 if fever_mode else 0.1
            
            output = self._model(
                prompt, 
                max_tokens=len(current_text) + 100, 
                stop=["\n", "User:", "###", "[/INST]"], 
                temperature=temp,
                echo=False
            )
            
            corrected_text = output['choices'][0]['text'].strip()
            if "[/INST]" in corrected_text:
                corrected_text = corrected_text.split("[/INST]")[-1].strip()

            # [Antibody V1] Aggressive Hallucination Filter
            # Removes meta-commentary like "(Inertie...)", "(Note...)", "(Correction...)"
            hallucination_markers = ["Inertie", "Note", "Correction", "Explanation", "Texte", "Text", "Valid", "Avvertissement", "Attention", "Le mot", "La phrase", "Word", "Meaning", "Sens"]
            for marker in hallucination_markers:
                corrected_text = re.sub(r'\(\s*' + marker + r'.*?\)', '', corrected_text, flags=re.IGNORECASE).strip()
            
            # Clean up double spaces resulting from removal
            corrected_text = re.sub(r'\s+', ' ', corrected_text).strip()

            # 3. Validation avancée (Sanity Check + Jaccard)
            if not self._is_safe_correction(text_segment, corrected_text, fever_mode=fever_mode):
                 print(f"⚠️ Correction rejetée (Safety Check - Fever={fever_mode}): '{text_segment}' -> '{corrected_text}'")
                 return text_segment
            
            # [V8] Si Fièvre et correction validée -> On log
            if fever_mode and corrected_text != text_segment:
                print(f"🌡️ FEVER REWRITE: '{text_segment}' -> '{corrected_text}'")
            
            # [Phase 27] Logic Guards (Strict Rules)
            # Enforce Logical Consistency even if LLM missed it
            corrected_text = self._apply_logic_guards(text_segment, corrected_text)
            
            return corrected_text

        except Exception as e:
            print(f"❌ Erreur d'inférence: {e}")
            return text_segment

    def _apply_logic_guards(self, original: str, corrected: str) -> str:
        """
        [Phase 27] Hard-coded rules to fix logical inconsistencies the LLM might miss.
        1. Common Words Capitalization: 'la Lune' -> 'la lune'
        2. Dialogue Structure: Restore lost dashes? (Dangerous, maybe just protect existing)
        """
        final = corrected
        
        # Rule 1: Fix Mid-Sentence Capitalization of Common Words (if not proper noun)
        # This is risky without a POS tagger, but we can do a dictionary check.
        # If 'Lune' is unknown but 'lune' is known, use 'lune'.
        
        words = final.split()
        if len(words) > 1:
            new_words = []
            for i, w in enumerate(words):
                # Skip first word (sentence start)
                if i == 0:
                    new_words.append(w)
                    continue
                    
                # If word is capitalized
                if w[0].isupper() and len(w) > 1:
                     # Check if it's a known proper noun?
                     # If 'lune' exists in dictionary but 'Lune' does not?
                     lower_w = w.lower()
                     if self.dictionary.validate(lower_w) and not self.dictionary.validate(w):
                         # High probability it's a mistake (e.g. 'la Lune')
                         new_words.append(lower_w)
                     else:
                         new_words.append(w)
                else:
                    new_words.append(w)
            final = " ".join(new_words)
            
        return final

    def _is_safe_correction(self, original: str, corrected: str, fever_mode: bool = False) -> bool:
        """
        Vérifie si la correction est sûre.
        Si fever_mode=True, on abaisse les seuils de Jaccard et d'Inertie.
        """
        if not corrected:
             return False
        
        # Tolérance longueur
        if abs(len(corrected) - len(original)) > len(original) * 0.5:
             return False

        # Tokenization basique
        def tokenize(text):
            clean = re.sub(r'[^\w\s]', ' ', text.lower())
            return set(clean.split())

        orig_tokens = tokenize(original)
        corr_tokens = tokenize(corrected)

        if not orig_tokens:
             return True

        intersection = orig_tokens.intersection(corr_tokens)

        # [V4] LE GARDIEN (Dictionary Veto)
        if self.dictionary:
            new_words = corr_tokens - orig_tokens
            for word in new_words:
                if len(word) > 2 and not self.dictionary.validate(word):
                     # [V8] En mode Fièvre, on est plus tolérant sur les "nouveaux" mots si le contexte l'exige?
                     # Non, le Gardien reste strict sur les Mots INCONNUS. On ne veut pas d'hallucination lexicale.
                     print(f"🛡️ VETO GARDIEN : Mot inventé/inconnu détecté '{word}' -> Correction rejetée.")
                     return False

        # SÉCURITÉ LINGUISTIQUE (Gardien des Langues)
        common_fr = {'le', 'la', 'les', 'et', 'est', 'un', 'une', 'des', 'dans'}
        common_en = {'the', 'and', 'is', 'in', 'of', 'to', 'for', 'with'}
        orig_fr_count = sum(1 for w in orig_tokens if w in common_fr)
        corr_en_count = sum(1 for w in corr_tokens if w in common_en)
        
        if orig_fr_count > 0 and corr_en_count > orig_fr_count:
            print(f"🚩 ALERTE TRADUCTION : Rejeté par le Gardien des Langues")
            return False

        # Seuil de ressemblance (Jaccard-ish)
        # Normal: 0.7 | Fièvre: 0.5
        jaccard_threshold = 0.5 if fever_mode else 0.7
        
        if len(orig_tokens) > 3:
             ratio = len(intersection) / len(orig_tokens)
             if ratio < jaccard_threshold:
                  # print(f"      [Safety] Low overlap ({ratio:.2f} < {jaccard_threshold})")
                  return False
        
        # [V5.1] PRINCIPE D'INERTIE (The Anchor)
        if self.dictionary:
            for word in orig_tokens:
                # 1. Le mot original est-il valide ?
                if len(word) > 3 and self.dictionary.validate(word):
                    # 2. Est-il présent dans la correction ?
                    if word in corr_tokens:
                        continue 
                    
                    # 3. S'il a disparu, est-ce pour une "bonne cause" (correction mineure) ?
                    match_found = False
                    for c_word in corr_tokens:
                        # Ratio Normal: 0.8 | Fièvre: 0.6 (Autorise "traduit" -> "conduit" ?)
                        # "traduit"/"conduit" = 0.57. Donc même 0.6 est limite.
                        # Mais 0.6 permet plus de souplesse.
                        sim_threshold = 0.6 if fever_mode else 0.8
                        sim = SequenceMatcher(None, word, c_word).ratio()
                        if sim > sim_threshold:
                            match_found = True
                            break
                    
                    if not match_found:
                         # En mode fievre, si on n'a pas trouvé de match, on accepte quand même LA PERTE du mot
                         # SI et SEULEMENT SI le mot était "suspect" ? Mais ici on sait qu'il est valide.
                         # Si le mot est valide, on le garde. Sauf si le contexte prouve qu'il est faux.
                         # L'IA a choisi de l'enlever.
                         # Si Fever=True, on fait confiance à l'IA ?
                         # On loggue juste un warning sans rejeter ?
                         if fever_mode:
                             print(f"⚓ INFO: Inertie relâchée sur '{word}' (Fever Mode)")
                             continue # On accepte la disparition
                         
                         print(f"⚓ OR VETO INERTIE : Tentative de modif mot valide '{word}' (non retrouvé ou trop modifié). Rejet.")
                         return False

        self._log_validated_correction(original, corrected)
        return True

    def _log_validated_correction(self, original: str, corrected: str):
        """
        Enregistre la correction validée en utilisant un alignement par DIFF
        pour n'extraire que les mots réellement modifiés (Apprentissage Chirurgical).
        """
        if not get_composite_key:
            return

        import json
        from datetime import datetime
        from difflib import SequenceMatcher
        
        orig_tokens = original.split()
        corr_tokens = corrected.split()
        
        # Utilisation de SequenceMatcher pour aligner les mots
        matcher = SequenceMatcher(None, orig_tokens, corr_tokens)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            # On ne s'intéresse qu'aux substitutions (replace)
            # 'replace' signifie qu'un bloc de mots a été remplacé par un autre
            if tag == 'replace':
                # Pour garder l'apprentissage "chirurgical", on ne loggue que si
                # c'est du 1-pour-1 ou si le nombre de mots est faible.
                # Cela évite de mémoriser des grosses reformulations.
                idx_orig = i1
                idx_corr = j1
                
                while idx_orig < i2 and idx_corr < j2:
                    o_word = orig_tokens[idx_orig]
                    c_word = corr_tokens[idx_corr]
                    
                    if o_word != c_word:
                        key = get_composite_key(o_word, original)
                        entry = {
                            "key": key,
                            "mot_source": o_word,
                            "mot_cible": c_word,
                            "contexte_brut": original,
                            "timestamp": datetime.now().isoformat(),
                            "confidence": 1.0
                        }
                        
                        self.session_log.append(entry)
                        
                        # Sauvegarde incrémentale
                        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
                        with open(self.log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    
                    idx_orig += 1
                    idx_corr += 1

    def _build_prompt(self, text: str, fever_mode: bool = False) -> str:
        """Construit le prompt avec instructions et exemples (RAG Dynamique)"""
        
        # 1. Recherche d'exemples dynamiques (RAG)
        dynamic_examples = self._lookup_knowledge(text)
        example_str = ""
        
        if dynamic_examples:
            example_str += "\n--- Exemples (Précédents) appris pertinents ---\n"
            for i, ex in enumerate(dynamic_examples):
                # On supporte les formats V5 (original/corrected) et V6 (mot_source/mot_cible)
                src = ex.get('original') or ex.get('mot_source')
                tgt = ex.get('corrected') or ex.get('mot_cible')
                example_str += f"Précédent {i+1}:\nEntrée: {src}\nSortie: {tgt}\n"
        
        # 2. Exemples statiques de base
        static_examples = """
--- Exemples Génériques ---
Exemple 1 (Typo simple):
Entrée: Le cbat boit du lait.
Sortie: Le chat boit du lait.

Exemple 2 (Fragment):
Entrée: -âcher ma mort.
Sortie: -racheter ma mort.
"""
        # [V20] Utilisation du template mutable
        # Note: ocr_knowledge est déjà inclus dans self.prompt_template
        base_prompt = f"{self.prompt_template}"
        
        if fever_mode:
            base_prompt += "\n>>> MODE FIÈVRE (DAREDEVIL) ACTIVÉ <<<\n"
            base_prompt += "INSTRUCTION PRIORITAIRE : Tu DOIS corriger toutes les erreurs visuelles (ex: 1'homme -> l'homme, c0mment -> comment) même si tu as un doute. SOIS AUDACIEUX. N'aie pas peur de modifier.\n"

        return f"""{base_prompt}

{example_str}
{static_examples}

Entrée: {text}
Sortie: [/INST]"""
