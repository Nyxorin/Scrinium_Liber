#!/usr/bin/env python3
"""
Phase 3: Corrections Avancées - Erreurs identifiées par analyse détaillée
Corrige les 2,568 erreurs OCR restantes après Phase 1+2
"""

from core.change_tracker import ChangeTracker, TrackedCorrector
import re


class Phase3CorrectionsAvancees:
    """
    Phase 3: Corrections avancées basées sur l'analyse réelle des erreurs.

    Cible:
    - 2,408 apostrophes typographiques (94% des erreurs)
    - 106 casse bizarre (4%)
    - 34 chiffres complexes (1.3%)
    - 20+ autres erreurs spécifiques
    """

    def __init__(self, tracker: ChangeTracker = None):
        self.tracker = tracker or ChangeTracker()
        self.corrector = TrackedCorrector(self.tracker)

    def apply(self, text: str) -> str:
        """Applique toutes les corrections de Phase 3."""
        print("=" * 80)
        print("🔧 PHASE 3: CORRECTIONS AVANCÉES")
        print("=" * 80)
        print()

        # 1. Apostrophes typographiques (PRIORITÉ #1 - 94% des erreurs!)
        print("📝 1/6 - Correction apostrophes typographiques...")
        text = self._fix_apostrophes(text)

        # 2. Chiffres complexes mélangés
        print("📝 2/6 - Correction chiffres complexes...")
        text = self._fix_complex_numbers(text)

        # 3. Casse bizarre
        print("📝 3/6 - Correction casse bizarre...")
        text = self._fix_weird_case(text)

        # 4. Ligatures mal lues
        print("📝 4/6 - Correction ligatures...")
        text = self._fix_ligatures(text)

        # 5. Accents incorrects
        print("📝 5/6 - Correction accents...")
        text = self._fix_accents(text)

        # 6. Mots spécifiques
        print("📝 6/6 - Correction mots spécifiques...")
        text = self._fix_specific_words(text)

        print()
        print("✅ Phase 3 terminée!")
        print(f"📊 {self.tracker.get_total_changes()} corrections effectuées")
        print()

        return text

    def _fix_apostrophes(self, text: str) -> str:
        """
        Corrige les apostrophes typographiques.

        IMPACT: ~2,408 corrections (94% des erreurs restantes!)

        Remplace ' (U+2019 RIGHT SINGLE QUOTATION MARK)
        par ' (U+0027 APOSTROPHE standard)
        """
        # Apostrophe typographique → apostrophe standard
        # U+2019 RIGHT SINGLE QUOTATION MARK → U+0027 APOSTROPHE
        text = self.corrector.apply_replacement(
            text,
            pattern="\u2019",  # RIGHT SINGLE QUOTATION MARK
            replacement="'",  # Standard apostrophe
            rule_name="Apostrophe typographique → standard",
            is_regex=False
        )

        # Autres variantes d'apostrophes
        apostrophes_variants = {
            '`': "'",  # Backtick
            "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
            "\u201B": "'",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK
            "\u2032": "'",  # PRIME
        }

        for variant, standard in apostrophes_variants.items():
            if variant in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=variant,
                    replacement=standard,
                    rule_name=f"Apostrophe variante ({variant}) → standard",
                    is_regex=False
                )

        return text

    def _fix_complex_numbers(self, text: str) -> str:
        """
        Corrige les chiffres complexes mélangés avec lettres.

        IMPACT: ~34 corrections
        """
        # Patterns spécifiques identifiés
        specific_fixes = {
            'q11eIques': 'quelques',
            '4ues': 'ques',  # "quelques" mal lu
            't48': 'tas',
            'paY7': 'pays',
            '1u': 'lu',
            '4e': 'de',
            '4IIons': 'Allons',
            '1100M': 'BOOM',
            '4ypnose': 'hypnose',
            'dess4P': 'dessaP',  # Probable "dessus" ou autre
            'iw0U': 'mou',
            'P4srasé': 'Parasé',
            'W11fainant': 'Malfainant',
            'l2eau': "l'eau",
        }

        for wrong, correct in specific_fixes.items():
            if wrong in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=re.escape(wrong),
                    replacement=correct,
                    rule_name=f"Chiffres complexes: {wrong} → {correct}",
                    is_regex=True
                )

        # Patterns génériques
        # 0 → O dans certains contextes
        text = self.corrector.apply_replacement(
            text,
            pattern=r'\b([A-Z]{2,})0([A-Z]{2,})\b',
            replacement=r'\1O\2',
            rule_name="0 → O dans mots majuscules",
            is_regex=True
        )

        # 1 → I ou l selon contexte
        text = self.corrector.apply_replacement(
            text,
            pattern=r'\b1([lm])\b',
            replacement=r'I\1',
            rule_name="1 → I en début de mot court",
            is_regex=True
        )

        # 7 → ?
        # Difficile sans contexte, on laisse pour l'instant

        return text

    def _fix_weird_case(self, text: str) -> str:
        """
        Corrige la casse bizarre (majuscules/minuscules mélangées).

        IMPACT: ~106 corrections
        """
        # Patterns spécifiques identifiés
        weird_cases = {
            'PrOvoquants': 'provoquants',
            'DePartment': 'Department',
            'SomALIE': 'SOMALIE',
            'NNavlSn': 'NNavISn',  # Pas sûr, mais probable
            'AberMY': 'Abernathy',  # Nom probable
            'VatiOnal': 'National',
            'eltAdireuFxoraoes': '',  # Charabia, probablement à supprimer
        }

        for wrong, correct in weird_cases.items():
            if wrong in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=re.escape(wrong),
                    replacement=correct,
                    rule_name=f"Casse bizarre: {wrong} → {correct}",
                    is_regex=True
                )

        # Pattern générique: Mots avec 3+ majuscules mélangées (sauf acronymes)
        # Détecte des patterns comme: SomALIE, PrOvoquants
        # Mais ignore: CIA, USA, NATO (acronymes valides)
        def fix_mixed_case(match):
            word = match.group(0)

            # Ignorer vrais acronymes (tout en majuscules, 2-5 lettres)
            if word.isupper() and 2 <= len(word) <= 5:
                return word

            # Ignorer noms propres normaux (1ère majuscule + reste minuscules)
            if word[0].isupper() and word[1:].islower():
                return word

            # Si 3+ majuscules dans un mot de 6+ lettres → probablement erreur
            maj_count = sum(1 for c in word if c.isupper())
            if len(word) >= 6 and maj_count >= 3:
                # Enregistrer changement
                # Heuristique: tout en minuscules (sauf 1ère lettre si début de phrase)
                corrected = word.lower()

                self.tracker.record_change(
                    rule_name="Casse bizarre (générique)",
                    original=word,
                    corrected=corrected,
                    context=match.string[max(0, match.start()-30):match.end()+30]
                )

                return corrected

            return word

        # Chercher mots avec majuscules mélangées
        # \b[A-Z][a-z]*([A-Z][a-z]*){2,}\b détecte au moins 3 segments Maj+minuscules
        text = re.sub(
            r'\b[A-Z][a-z]*[A-Z][a-z]*[A-Z][a-zA-Z]*\b',
            fix_mixed_case,
            text
        )

        return text

    def _fix_ligatures(self, text: str) -> str:
        """
        Corrige les ligatures mal lues.

        IMPACT: ~4 corrections
        """
        ligatures = {
            'fhŒtes': 'faites',
            'OŸ': 'Où',
            'Œ': 'Oe',  # Générique
            'œ': 'oe',  # Générique
            'Ÿ': 'Y',   # Générique
        }

        for wrong, correct in ligatures.items():
            if wrong in text:
                text = self.corrector.apply_replacement(
                    text,
                    pattern=re.escape(wrong),
                    replacement=correct,
                    rule_name=f"Ligature: {wrong} → {correct}",
                    is_regex=True
                )

        return text

    def _fix_accents(self, text: str) -> str:
        """
        Corrige les accents incorrects.

        IMPACT: ~6 corrections
        """
        accent_fixes = {
            r'\bch[çc]ne\b': 'chaîne',
            r'\bt[èe]te\b': 'tête',
            r'\bpr[o0][xX][io]mit[ée]': 'proximité',
            r'\bbr[uû]lan[ít]': 'brûlant',
            r'\bent[àa]nts?\b': 'enfants',
        }

        for pattern, correct in accent_fixes.items():
            text = self.corrector.apply_replacement(
                text,
                pattern=pattern,
                replacement=correct,
                rule_name=f"Accent incorrect → {correct}",
                is_regex=True
            )

        return text

    def _fix_specific_words(self, text: str) -> str:
        """
        Corrige des mots spécifiques identifiés.

        IMPACT: ~20 corrections
        """
        specific_words = {
            'vestifi': 'vestiti',
            'Sornalis': 'Somaliens',
            "n'esse": 'messe',
            r'\blm\b': 'les',  # "lm" → "les" (56 occurrences!)
            r'\bim\b': 'il',   # "im" → "il" (386 occurrences!)
            'agzessivement': 'agressivement',
            r'\bagz': 'agr',   # "agz" → "agr"
        }

        for pattern, correct in specific_words.items():
            text = self.corrector.apply_replacement(
                text,
                pattern=pattern,
                replacement=correct,
                rule_name=f"Mot spécifique: {pattern} → {correct}",
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
    """Test de Phase 3."""
    # Test simple
    test_text = """
    Il l'a dit qu'il n'y a pas de problème.
    Les vestifi verde sont là.
    Il y a 4ues personnes.
    C'est PrOvoquants!
    OŸ est-il?
    """

    print("Texte AVANT:")
    print(test_text)
    print()

    phase3 = Phase3CorrectionsAvancees()
    corrected = phase3.apply(test_text)

    print()
    print("Texte APRÈS:")
    print(corrected)
    print()

    print(phase3.get_report())


if __name__ == "__main__":
    main()
