#!/usr/bin/env python3
"""
Phase 5: Corrections semi-automatiques avec validation
- Chiffres mélangés
- Caractères spéciaux
- Doublons de lettres
- Casse bizarre
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.change_tracker import ChangeTracker, TrackedCorrector
from core.dictionary import FrenchDictionary


class Phase5SemiAuto:
    """Corrections semi-automatiques avec validation dictionnaire."""

    def __init__(self, tracker: ChangeTracker = None):
        self.tracker = tracker or ChangeTracker()
        self.corrector = TrackedCorrector(self.tracker)
        self.dictionary = None

    def apply(self, text: str) -> str:
        """Applique toutes les corrections semi-automatiques."""
        print("=" * 80)
        print("🔧 PHASE 5: CORRECTIONS SEMI-AUTOMATIQUES")
        print("=" * 80)
        print()

        # Charger dictionnaire
        print("📚 Chargement du dictionnaire...")
        self.dictionary = FrenchDictionary()
        print(f"✓ {len(self.dictionary.words):,} mots chargés")
        print()

        # 1. Caractères spéciaux (facile, confiance 95%)
        print("📝 1/4 - Correction caractères spéciaux...")
        text = self._fix_special_chars(text)

        # 2. Chiffres mélangés (moyen, confiance 85%)
        print("📝 2/4 - Correction chiffres mélangés...")
        text = self._fix_number_letter_mix(text)

        # 3. Doublons de lettres (facile, confiance 80%)
        print("📝 3/4 - Correction doublons de lettres...")
        text = self._fix_letter_duplicates(text)

        # 4. Casse bizarre (moyen, confiance 70%)
        print("📝 4/4 - Correction casse bizarre...")
        text = self._fix_weird_case(text)

        print()
        print("✅ Phase 5 terminée!")
        print(f"📊 {self.tracker.get_total_changes()} corrections effectuées")
        print()

        return text

    def _fix_special_chars(self, text: str) -> str:
        """Corrige les caractères spéciaux."""
        # Patterns de remplacement
        replacements = {
            r'=': '-',  # = → -
            r'\[': '(',  # [ → (
            r'\]': ')',  # ] → )
        }

        # D'abord, essayer des patterns spécifiques connus
        specific_fixes = {
            "tas=9": "otages",  # Contexte: "les otages"
            "Atv=ent": "Auvent",
            "L=d-Rover": "Land-Rover",
            "souff[a": "souffla",
        }

        for wrong, correct in specific_fixes.items():
            if wrong in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=re.escape(wrong),
                    replacement=correct,
                    rule_name=f"Caractère spécial: {wrong} → {correct}",
                    is_regex=True
                )

        # Ensuite, patterns génériques
        for special, replacement in replacements.items():
            # Ne pas remplacer aveuglément - chercher dans contexte de mot
            pattern = rf'\b\w*{special}\w*\b'
            matches = list(re.finditer(pattern, text))

            for match in matches:
                word = match.group()
                candidate = word.replace(special, replacement)

                # Valider avec dictionnaire
                if self.dictionary.validate(candidate.lower()):
                    text = text[:match.start()] + candidate + text[match.end():]
                    self.tracker.record_change(
                        rule_name=f"Caractère spécial ({special}) validé par dictionnaire",
                        original=word,
                        corrected=candidate,
                        context=text[max(0, match.start()-40):match.end()+40]
                    )

        return text

    def _fix_number_letter_mix(self, text: str) -> str:
        """Corrige les chiffres mélangés avec lettres."""

        # Patterns de substitution chiffre → lettre
        digit_to_letter = {
            '0': ['O', 'o'],
            '1': ['l', 'I', 'i'],
            '4': ['A', 'a'],
            '7': ['T', 't'],
            '8': ['B'],
            '9': ['g', 'q'],
        }

        # Pattern: mots avec chiffres
        pattern = r'\b[a-zA-Zàâäæçèéêëìíîïòóôöùúûü]*\d+[a-zA-Zàâäæçèéêëìíîïòóôöùúûü]*\b'

        for match in re.finditer(pattern, text):
            word = match.group()

            # Ignorer dates
            if re.match(r'^(19|20)\d{2}$', word):
                continue

            # Ignorer numéros purs
            if word.isdigit():
                continue

            # Générer candidats en remplaçant chiffres
            candidates = self._generate_candidates(word, digit_to_letter)

            # Valider avec dictionnaire
            valid_candidates = []
            for candidate in candidates:
                if self.dictionary.validate(candidate.lower()):
                    valid_candidates.append(candidate)

            # Si exactement 1 candidat valide, appliquer
            if len(valid_candidates) == 1:
                corrected = valid_candidates[0]
                # Remplacer dans le texte
                text = text[:match.start()] + corrected + text[match.end():]

                self.tracker.record_change(
                    rule_name="Chiffres mélangés → validé par dictionnaire",
                    original=word,
                    corrected=corrected,
                    context=text[max(0, match.start()-40):match.end()+40],
                    line_num=text[:match.start()].count('\n') + 1
                )

        return text

    def _generate_candidates(self, word: str, substitutions: dict, max_depth=2) -> list:
        """Génère tous les candidats en remplaçant chiffres par lettres."""
        if max_depth == 0:
            return [word]

        candidates = set([word])

        for digit, letters in substitutions.items():
            if digit in word:
                for letter in letters:
                    new_word = word.replace(digit, letter, 1)
                    candidates.add(new_word)

                    # Récursif pour substitutions multiples
                    if max_depth > 1:
                        for sub_candidate in self._generate_candidates(new_word, substitutions, max_depth - 1):
                            candidates.add(sub_candidate)

        return list(candidates)

    def _fix_letter_duplicates(self, text: str) -> str:
        """Corrige les répétitions excessives de lettres."""

        # Pattern: triple lettres ou plus
        pattern = r'\b\w*([a-zàâäæçèéêëìíîïòóôöùúûü])\1{2,}\w*\b'

        for match in re.finditer(pattern, text, re.IGNORECASE):
            word = match.group()

            # Ignorer chiffres romains (III, VIII, XIII, etc.)
            if re.match(r'^[IVXLCDM]+$', word):
                continue

            # Tester avec double, puis simple
            letter = match.group(1)
            triple_pattern = letter + letter + letter

            # Essayer double
            candidate_double = word.replace(triple_pattern, letter + letter)

            if self.dictionary.validate(candidate_double.lower()):
                text = text[:match.start()] + candidate_double + text[match.end():]
                self.tracker.record_change(
                    rule_name="Doublons de lettres réduits",
                    original=word,
                    corrected=candidate_double,
                    context=text[max(0, match.start()-40):match.end()+40]
                )
                continue

            # Essayer simple
            candidate_single = word.replace(triple_pattern, letter)

            if self.dictionary.validate(candidate_single.lower()):
                text = text[:match.start()] + candidate_single + text[match.end():]
                self.tracker.record_change(
                    rule_name="Doublons de lettres réduits",
                    original=word,
                    corrected=candidate_single,
                    context=text[max(0, match.start()-40):match.end()+40]
                )

        return text

    def _fix_weird_case(self, text: str) -> str:
        """Corrige la casse bizarre."""

        # Patterns spécifiques connus
        specific_fixes = {
            'PUYs': 'pays',
            'PenWM': 'Pendant',
            'VNOn': 'Non',
            'vOulez': 'voulez',
            'vOus': 'vous',
            'exPression': 'expression',
            'afTirmer': 'affirmer',
            'municiPale': 'municipale',
            'riCain': 'ricain',
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
                    rule_name=f"Casse bizarre: {wrong} → {correct}",
                    is_regex=True
                )

        return text

    def get_report(self) -> str:
        """Retourne le rapport des corrections."""
        return self.tracker.generate_report()

    def save_detailed_report(self, filepath: str):
        """Sauvegarde un rapport détaillé."""
        self.tracker.save_detailed_report(filepath)


def main():
    """Test de Phase 5."""
    test_text = """
    Il y a des tas=9 personnes.
    Le L=d-Rover est là.
    C'est deviiiait difficile.
    """

    print("Texte AVANT:")
    print(test_text)
    print()

    phase5 = Phase5SemiAuto()
    corrected = phase5.apply(test_text)

    print()
    print("Texte APRÈS:")
    print(corrected)
    print()

    print(phase5.get_report())


if __name__ == "__main__":
    main()
