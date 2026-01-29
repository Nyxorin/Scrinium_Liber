#!/usr/bin/env python3
"""
EPUB Cleaner Complete - Nettoyeur EPUB complet et automatique.
Version refactorisée utilisant les modules CORE et les correcteurs spécialisés.
"""

import re
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pathlib import Path
from core.dictionary import FrenchDictionary
from core.text_processor import TextProcessor
from correctors.deterministic_corrector import DeterministicCorrector
from correctors.semantic_corrector import SemanticCorrector
from core.knowledge_manager import KnowledgeManager
import concurrent.futures
import copy


class CompleteEPUBCleaner:
    """Nettoyeur EPUB complet utilisant le pipeline de correction standardisé."""

    def __init__(self, epub_path, dictionary_path="dictionnaire_francais.pkl"):
        """
        Initialise le nettoyeur EPUB.

        Args:
            epub_path: Chemin vers le fichier EPUB
            dictionary_path: Chemin vers le dictionnaire Megalex
            limit: Nombre maximum de chapitres à traiter (optionnel)
        """
        self.epub_path = epub_path
        self.limit = None
        self.book = None
        self.dictionary = FrenchDictionary(dictionary_path)
        self.corrector = DeterministicCorrector()
        self.semantic = SemanticCorrector() # Singleton, chargera le modèle si présent
        self.repeated_texts = []
        
        # [V6] Mémoire de correction (RAG & Cache)
        self.knowledge = KnowledgeManager()

    def load_epub(self):
        """Charge le fichier EPUB"""
        try:
            self.book = epub.read_epub(self.epub_path)
            
            # [V6] Extraction du titre pour le log de session
            title = "Unknown_Book"
            titles = self.book.get_metadata('DC', 'title')
            if titles:
                title = titles[0][0]
            
            print(f"✓ EPUB chargé: {title} ({self.epub_path})")
            
            # Initialisation de la session de log avec le titre
            self.semantic.initialize_session(title)
            
            return True
        except Exception as e:
            print(f"✗ Erreur lors du chargement de l'EPUB: {e}")
            return False

    def detect_repeated_texts(self):
        """
        Détecte les textes qui apparaissent de manière répétitive
        (titres de livre, en-têtes, pieds de page).
        """
        from collections import Counter
        print("\n🔍 Détection des textes répétitifs (titres, en-têtes)...")

        text_occurrences = Counter()
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    content = item.get_content().decode('utf-8')
                    text = TextProcessor.extract_from_html(content)
                    lines = [line.strip() for line in text.split('\n') if line.strip()]

                    for line in lines:
                        # [V7.1] Header Killer: On relâche la contrainte majuscule
                        # Si le texte se répète souvent (titre livre, chapitre), c'est un header.
                        if 3 < len(line) < 150:
                             text_occurrences[line] += 1
                except Exception:
                    continue

        self.repeated_texts = [text for text, count in text_occurrences.items() if count >= 3]
        if self.repeated_texts:
            print(f"✓ {len(self.repeated_texts)} texte(s) répétitif(s) détecté(s)")
        return self.repeated_texts

    def clean_html_content(self, html_content):
        """Nettoie le contenu HTML d'un chapitre."""
        # Extraire le texte
        text = TextProcessor.extract_from_html(html_content)
        
        # Supprimer les titres répétitifs
        for repeated in self.repeated_texts:
            text = text.replace(repeated, "")

        # Appliquer les corrections déterministes
        cleaned_text = self.corrector.correct(text)

        # Appliquer la correction sémantique (LLM) par paragraphe
        # On ne traite que si le modèle est chargé
        if self.semantic._model:
            print(f"    🤖 Optimisation Sémantique en cours ({len(html_content)} octets)...")
            lines = cleaned_text.split('\n')
            final_lines = []
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    final_lines.append(line)
                    continue

                # --- SMART FILTER ---
                # 1. Si la ligne est courte (< 20 chars), on ignore (souvent des titres ou débris)
                if len(stripped) < 20:
                    final_lines.append(line)
                    continue

                # 2. Vérification Dictionnaire (Rapide)
                words = [w for w in stripped.split() if len(w) > 3] # On ignore les mots courts
                if not words:
                    final_lines.append(line)
                    continue
                
                # On compte combien de mots semblent invalides
                unknown_count = 0
                temp_line = stripped
                
                for w in words:
                    clean_w = w.strip(".,;:?!'\"()[]-")
                    if not self.dictionary.validate(clean_w):
                        # [V6] Tentative de Cache Hit (V7: avec confiance)
                        cache_hit = self.knowledge.lookup(clean_w, stripped)
                        if cache_hit and cache_hit.get('can_fast_track'):
                            # print(f"      [FAST-TRACK] {clean_w} -> {cache_hit['mot_cible']}")
                            temp_line = temp_line.replace(clean_w, cache_hit['mot_cible'])
                        else:
                            # Pas de cache ou confiance insuffisante -> Nécessite le LLM
                            unknown_count += 1
                
                # 3. Décision : On appelle le LLM seulement si > 0 mot inconnu restant
                if unknown_count > 0:
                    corrected = self.semantic.correct_segment(line)
                    final_lines.append(corrected)
                elif temp_line != stripped:
                    # Correction effectuée via Cache uniquement
                    final_lines.append(temp_line)
                else:
                    # Tout est connu ou déjà ignoré
                    final_lines.append(line)
            
            cleaned_text = '\n'.join(final_lines)
        
        # Reconstruire le HTML
        return TextProcessor.rebuild_html(cleaned_text, html_content)

    def process_epub(self, max_workers=1):
        """Traite tous les documents de l'EPUB (Support Parallèle)."""
        if not self.book:
            return False

        self.detect_repeated_texts()

        print(f"\n🧹 Nettoyage des chapitres (Workers: {max_workers})...")
        
        # Identification des chapitres à traiter
        items_to_process = []
        limit_counter = 0
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if self.limit and limit_counter >= self.limit:
                    break
                items_to_process.append(item)
                limit_counter += 1

        if max_workers <= 1:
            # Mode Séquentiel (Original)
            for item in items_to_process:
                try:
                    content = item.get_content().decode('utf-8')
                    cleaned_content = self.clean_html_content(content)
                    item.set_content(cleaned_content.encode('utf-8'))
                    print(f"✓ Chapitre nettoyé: {item.get_name()}")
                except Exception as e:
                    print(f"✗ Erreur sur {item.get_name()}: {e}")
        else:
            # Mode Parallèle (V7)
            print(f"🚀 Lancement du pool de {max_workers} processus...")
            # On doit extraire les données pour les envoyer aux workers
            # car l'objet epub.Item n'est pas forcément picklable facilement sans perte.
            tasks = []
            for item in items_to_process:
                tasks.append({
                    'name': item.get_name(),
                    'content': item.get_content().decode('utf-8'),
                    'repeated_texts': self.repeated_texts,
                    'log_path': self.semantic.log_path # On transmet le chemin du log
                })

            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers, initializer=init_worker) as executor:
                # Utilisation d'une fonction statique ou globale pour le worker
                futures = {executor.submit(worker_clean_chapter, task): task['name'] for task in tasks}
                
                for future in concurrent.futures.as_completed(futures):
                    item_name = futures[future]
                    try:
                        result_content = future.result()
                        # On retrouve l'item original pour mettre à jour son contenu
                        for item in items_to_process:
                            if item.get_name() == item_name:
                                item.set_content(result_content.encode('utf-8'))
                                break
                        print(f"✓ Chapitre nettoyé (parallèle): {item_name}")
                    except Exception as e:
                        print(f"✗ Erreur parallèle sur {item_name}: {e}")

        print(f"\n✓ {len(items_to_process)} chapitre(s) traité(s)")
        return True

    def save_epub(self, output_path):
        """Sauvegarde l'EPUB nettoyé"""
        try:
            epub.write_epub(output_path, self.book)
            print(f"✓ EPUB sauvegardé: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde: {e}")
            return False

    def clean(self, output_path, max_workers=1):
        """Pipeline complet de nettoyage."""
        print("=" * 80)
        print("🚀 EPUB CLEANER COMPLETE (V7 Parallel)")
        print("=" * 80)
        
        if self.load_epub() and self.process_epub(max_workers=max_workers) and self.save_epub(output_path):
            print("\n✅ Nettoyage terminé avec succès !")
            return True
        return False

# Global variable for worker processes
ner_agent = None

def init_worker():
    """Initialise les ressources persistantes du worker (NER Agent, Corrector Singleton)."""
    import os
    global ner_agent
    from core.ner_agent import NERAgent
    # Chaque worker lance son propre daemon (persistent)
    print(f"🔧 Worker {os.getpid()} initialise son NER Agent...")
    ner_agent = NERAgent(use_flaubert=True)

def worker_clean_chapter(task):
    """
    Fonction globale pour le worker (doit être picklable).
    Utilise les agents initialisés via init_worker ou les crée si besoin.
    """
    # Imports locaux pour éviter les fuites
    from correctors.deterministic_corrector import DeterministicCorrector
    from correctors.semantic_corrector import SemanticCorrector
    from core.dictionary import FrenchDictionary
    from core.knowledge_manager import KnowledgeManager
    from core.text_processor import TextProcessor
    # [V8] Modules Immunitaires
    from core.immune_system import ImmuneSystem
    from core.macrophage import Macrophage

    # On récupère l'agent global
    global ner_agent
    
    # Init autres agents (Singletons ou légers)
    corrector = DeterministicCorrector()
    semantic = SemanticCorrector() # Singleton
    if task.get('log_path'):
        semantic.log_path = task['log_path']
    
    dictionary = FrenchDictionary()
    knowledge = KnowledgeManager()
    immune = ImmuneSystem()
    macro = Macrophage()
    
    # Fallback si init_worker n'a pas tourné (ex: mode séquentiel)
    if ner_agent is None:
        from core.ner_agent import NERAgent
        ner_agent = NERAgent(use_flaubert=True)
    
    html_content = task['content']
    repeated_texts = task['repeated_texts']
    
    # Reproduction de la logique de clean_html_content (simplifiée pour le worker)
    text = TextProcessor.extract_from_html(html_content)
    for repeated in repeated_texts:
        text = text.replace(repeated, "")

    cleaned_text = corrector.correct(text)

    # [V8] IMMUNE SYSTEM ACTIVATION 🧬
    # 1. Antibodies (Blacklist & Corrections rapides)
    cleaned_text = immune.attack(cleaned_text)

    # 2. Macrophages (Word Splitter)
    # On applique la digestion sur chaque mot identifié par regex (préserve la ponctuation)
    cleaned_text = re.sub(r'\b\p{L}+\b' if False else r'\b\w+\b', lambda m: macro.digest(m.group(0)), cleaned_text)

    # Note: 'ner_agent' est déjà initialisé (global)
    
    if semantic._model:
        lines = cleaned_text.split('\n')
        final_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or len(stripped) < 20:
                final_lines.append(line)
                continue

            words = [w for w in stripped.split() if len(w) > 3]
            if not words:
                final_lines.append(line)
                continue

            unknown_count = 0
            word_count = len(words)
            temp_line = stripped
            for w in words:
                clean_w = w.strip(".,;:?!'\"()[]-")
                if not dictionary.validate(clean_w):
                    # [V8.1] NER Check 🕵️‍♂️ (Via ner_agent global)
                    # Si c'est un Nom Propre (Malko, Abdi, etc.), ce n'est PAS une erreur.
                    is_proper_noun = False
                    if clean_w[0].isupper(): 
                        # On utilise l'agent global
                        analysis = ner_agent.analyze(clean_w, stripped)
                        if analysis.get("is_proper_noun"):
                            is_proper_noun = True
                    
                    if is_proper_noun:
                        continue # On passe (Validé par NER)

                    cache_hit = knowledge.lookup(clean_w, stripped)
                    if cache_hit and cache_hit.get('can_fast_track'):
                        temp_line = temp_line.replace(clean_w, cache_hit['mot_cible'])
                    else:
                        unknown_count += 1
            
            # [V8] Calcul de la "Fièvre" (Taux d'erreur)
            unknown_ratio = unknown_count / word_count if word_count > 0 else 0
            fever_mode = unknown_ratio > 0.15 # Si + de 15% de mots inconnus -> Fièvre
            
            if unknown_count > 0:
                corrected = semantic.correct_segment(line, fever_mode=fever_mode)
                final_lines.append(corrected)
            elif temp_line != stripped:
                final_lines.append(temp_line)
            else:
                final_lines.append(line)
        cleaned_text = '\n'.join(final_lines)

    return TextProcessor.rebuild_html(cleaned_text, html_content)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python epub_cleaner_complete.py <input.epub> <output.epub> [limit]")
        sys.exit(1)
    
    cleaner = CompleteEPUBCleaner(sys.argv[1])
    
    limit = None
    if len(sys.argv) > 3:
        try:
            limit = int(sys.argv[3])
            cleaner.limit = limit
            print(f"🎯 Limite fixée à {cleaner.limit} chapitres")
        except ValueError:
            print("⚠️ Limite invalide, ignorée")
            
    # [V7] Option pour les workers (par défaut 2 pour le livre complet ou limit > 1)
    workers = 2 
    if limit and limit == 1:
        workers = 1 # Debug mode mono-thread si 1 seul chapitre demandé
        
    print(f"🚀 Mode Parallèle activé : {workers} workers")

    cleaner.clean(sys.argv[2], max_workers=workers)
