#!/usr/bin/env python3
"""
Phase 6: Corrections assistées (suggérer + valider)
- Accents suspects
- Mots collés
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.change_tracker import ChangeTracker, TrackedCorrector
from core.dictionary import FrenchDictionary


class Phase6Assistee:
    """Corrections assistées avec suggestions."""

    def __init__(self, tracker: ChangeTracker = None):
        self.tracker = tracker or ChangeTracker()
        self.corrector = TrackedCorrector(self.tracker)
        self.dictionary = None

    def apply(self, text: str, auto_mode: bool = True) -> str:
        """
        Applique les corrections assistées.

        Args:
            text: Texte à corriger
            auto_mode: Si True, applique automatiquement corrections haute confiance
        """
        print("=" * 80)
        print("🔧 PHASE 6: CORRECTIONS ASSISTÉES")
        print("=" * 80)
        print()

        # Charger dictionnaire
        print("📚 Chargement du dictionnaire...")
        self.dictionary = FrenchDictionary()
        print(f"✓ {len(self.dictionary.words):,} mots chargés")
        print()

        # 1. Accents suspects
        print("📝 1/2 - Correction accents suspects...")
        text = self._fix_wrong_accents(text, auto_mode)

        # 2. Mots collés
        print("📝 2/2 - Correction mots collés...")
        text = self._fix_merged_words(text, auto_mode)

        print()
        print("✅ Phase 6 terminée!")
        print(f"📊 {self.tracker.get_total_changes()} corrections effectuées")
        print()

        return text

    def _fix_wrong_accents(self, text: str, auto_mode: bool) -> str:
        """Corrige les accents suspects."""

        # Patterns spécifiques identifiés
        specific_fixes = {
            "bliçité": "publicité",
            "trçnait": "traînait",
            "merçenai": "mercenaire",
        }

        for wrong, correct in specific_fixes.items():
            if wrong in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=re.escape(wrong),
                    replacement=correct,
                    rule_name=f"Accent corrigé: {wrong} → {correct}",
                    is_regex=True
                )

        # Pattern générique: ç sans voyelle après
        pattern = r'\b\w*ç(?![aouàâäèéêëìíîïòóôöùúûü])\w*\b'

        for match in re.finditer(pattern, text):
            word = match.group()

            # Tester variantes
            candidates = [
                word.replace('ç', 'c'),
                word.replace('ç', ' '),
                word.replace('ç', ''),
            ]

            valid = []
            for candidate in candidates:
                if candidate and self.dictionary.validate(candidate.lower()):
                    valid.append(candidate)

            # Si auto_mode et 1 seul candidat, appliquer
            if auto_mode and len(valid) == 1:
                corrected = valid[0]
                text = text[:match.start()] + corrected + text[match.end():]

                self.tracker.record_change(
                    rule_name="Accent ç suspect → corrigé",
                    original=word,
                    corrected=corrected,
                    context=text[max(0, match.start()-40):match.end()+40]
                )

        return text

    def _fix_merged_words(self, text: str, auto_mode: bool) -> str:
        """Corrige les mots collés (minuscule+Majuscule)."""

        # Patterns spécifiques connus
        specific_fixes = {
            'socialisatiOn': 'socialisation',
            'vOulez': 'voulez',
            'vOus': 'vous',
            'exPression': 'expression',
            'afTirmer': 'affirmer',
            'municiPale': 'municipale',
            'riCain': 'ricain',  # Probablement "américain"
            'rattaChement': 'rattachement',
            'déPendent': 'dépendent',
            'aftWre': 'affaire',
        }

        for wrong, correct in specific_fixes.items():
            if wrong in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=re.escape(wrong),
                    replacement=correct,
                    rule_name=f"Mot collé: {wrong} → {correct}",
                    is_regex=True
                )

        # Pattern générique: mots avec majuscule interne
        pattern = r'\b([a-z]+)([A-Z][a-z]+)\b'

        for match in re.finditer(pattern, text):
            full_word = match.group(0)
            part1 = match.group(1)
            part2 = match.group(2)

            # Option 1: tout en minuscules
            candidate_lower = full_word.lower()

            # Option 2: séparer
            candidate_split = part1 + ' ' + part2.lower()

            valid_candidates = []

            if self.dictionary.validate(candidate_lower):
                valid_candidates.append(candidate_lower)

            # Pour split, vérifier les deux parties
            if self.dictionary.validate(part1) and self.dictionary.validate(part2.lower()):
                valid_candidates.append(candidate_split)

            # Si auto_mode et 1 seul candidat, appliquer
            if auto_mode and len(valid_candidates) == 1:
                corrected = valid_candidates[0]
                text = text[:match.start()] + corrected + text[match.end():]

                self.tracker.record_change(
                    rule_name="Casse interne corrigée",
                    original=full_word,
                    corrected=corrected,
                    context=text[max(0, match.start()-40):match.end()+40]
                )

        return text

    def get_report(self) -> str:
        """Retourne le rapport des corrections."""
        return self.tracker.generate_report()

    def save_detailed_report(self, filepath: str):
        """Sauvegarde un rapport détaillé."""
        self.tracker.save_detailed_report(filepath)


def main():
    """Test de Phase 6."""
    test_text = """
    C'est de la bliçité.
    Il vOulez partir.
    """

    print("Texte AVANT:")
    print(test_text)
    print()

    phase6 = Phase6Assistee()
    corrected = phase6.apply(test_text, auto_mode=True)

    print()
    print("Texte APRÈS:")
    print(corrected)
    print()

    print(phase6.get_report())


if __name__ == "__main__":
    main()
