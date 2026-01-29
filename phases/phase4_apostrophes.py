#!/usr/bin/env python3
"""
Phase 4: Correction des apostrophes non-standard
IMPACT: 3,644 erreurs (47% du total)
CONFIANCE: 100%
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.change_tracker import ChangeTracker, TrackedCorrector


class Phase4Apostrophes:
    """Correction des apostrophes non-standard."""

    def __init__(self, tracker: ChangeTracker = None):
        self.tracker = tracker or ChangeTracker()
        self.corrector = TrackedCorrector(self.tracker)

    def apply(self, text: str) -> str:
        """Applique toutes les corrections d'apostrophes."""
        print("=" * 80)
        print("🔧 PHASE 4: APOSTROPHES NON-STANDARD")
        print("=" * 80)
        print()
        print("🎯 OBJECTIF: Corriger ~3,644 apostrophes")
        print("🎯 CONFIANCE: 100%")
        print("🎯 MÉTHODE: Remplacement automatique 1:1")
        print()

        # Toutes les variantes d'apostrophes à corriger
        apostrophe_variants = {
            "\u2019": "RIGHT SINGLE QUOTATION MARK",     # ' → '
            "\u2018": "LEFT SINGLE QUOTATION MARK",      # ' → '
            "\u201B": "SINGLE HIGH-REVERSED-9",          # ‛ → '
            "\u2032": "PRIME",                            # ′ → '
            "\u02BC": "MODIFIER LETTER APOSTROPHE",      # ʼ → '
            "`": "GRAVE ACCENT (backtick)",              # ` → '
            "´": "ACUTE ACCENT",                          # ´ → '
        }

        total_before = len(text)

        print("📝 Correction des variantes d'apostrophes...")
        print()

        for variant_char, variant_name in apostrophe_variants.items():
            count_before = text.count(variant_char)

            if count_before > 0:
                print(f"   • {variant_name}: {count_before} occurrences")

                text = self.corrector.apply_replacement(
                    text,
                    pattern=variant_char,
                    replacement="'",
                    rule_name=f"Apostrophe {variant_name} → standard",
                    is_regex=False
                )

        print()
        print("✅ Phase 4 terminée!")
        print(f"📊 {self.tracker.get_total_changes()} corrections effectuées")
        print()

        return text

    def get_report(self) -> str:
        """Retourne le rapport des corrections."""
        return self.tracker.generate_report()

    def save_detailed_report(self, filepath: str):
        """Sauvegarde un rapport détaillé."""
        self.tracker.save_detailed_report(filepath)


def main():
    """Test de Phase 4."""
    test_text = """
    Il l'a dit qu'il n'y a pas de problème.
    C'est l'océan qui est là.
    Aujourd'hui, c'est difficile.
    """

    print("Texte AVANT:")
    print(test_text)
    print()

    phase4 = Phase4Apostrophes()
    corrected = phase4.apply(test_text)

    print()
    print("Texte APRÈS:")
    print(corrected)
    print()

    print(phase4.get_report())


if __name__ == "__main__":
    main()
