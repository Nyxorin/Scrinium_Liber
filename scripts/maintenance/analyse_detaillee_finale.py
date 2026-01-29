#!/usr/bin/env python3
"""
Analyse détaillée et exhaustive du fichier FINAL.
Identifie TOUTES les erreurs restantes avec contexte et suggestions de correction.
"""

import re
from pathlib import Path
from collections import Counter, defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent))

from core.dictionary import FrenchDictionary


class DetailedErrorAnalyzer:
    """Analyse exhaustive des erreurs avec suggestions de correction."""

    def __init__(self):
        self.dictionary = None
        self.errors = defaultdict(list)
        self.suggestions = {}

    def analyze(self, text):
        """Analyse complète du texte."""
        print("📚 Chargement du dictionnaire...")
        self.dictionary = FrenchDictionary()
        print(f"✓ {len(self.dictionary.words):,} mots chargés\n")

        print("🔍 Analyse en cours...\n")

        # 1. Chiffres dans mots
        self._find_numbers_in_words(text)

        # 2. Caractères spéciaux
        self._find_special_chars(text)

        # 3. Mots collés
        self._find_merged_words(text)

        # 4. Doublons de lettres
        self._find_letter_duplicates(text)

        # 5. Casse bizarre
        self._find_weird_case(text)

        # 6. Ligatures
        self._find_ligatures(text)

        # 7. Ponctuation bizarre
        self._find_weird_punctuation(text)

        # 8. Mots courts suspects (lm, im, etc.)
        self._find_suspicious_short_words(text)

        # 9. Accents suspects
        self._find_accent_issues(text)

        # 10. Espaces manquants/en trop
        self._find_spacing_issues(text)

    def _find_numbers_in_words(self, text):
        """Trouve chiffres mélangés avec lettres + suggère corrections."""
        pattern = r'\b[a-zA-Zàâäæçèéêëìíîïòóôöùúûü]*\d+[a-zA-Zàâäæçèéêëìíîïòóôöùúûü]*\b'

        digit_to_letter = {
            '0': ['O', 'o'],
            '1': ['l', 'I', 'i'],
            '4': ['A', 'a'],
            '7': ['T', 't'],
            '8': ['B', 'b'],
            '9': ['g', 'q'],
        }

        for match in re.finditer(pattern, text):
            word = match.group()

            # Ignorer dates
            if re.match(r'^(19|20)\d{2}$', word):
                continue

            # Ignorer numéros purs
            if word.isdigit():
                continue

            # Contexte
            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-60):min(len(text), start+60)]

            # Générer suggestions
            suggestions = self._generate_word_suggestions(word, digit_to_letter)

            self.errors['chiffres_dans_mots'].append({
                'word': word,
                'line': line_num,
                'context': context,
                'suggestions': suggestions,
                'position': start
            })

    def _generate_word_suggestions(self, word, substitutions):
        """Génère suggestions de correction pour mot avec chiffres."""
        candidates = []

        # Essayer toutes les substitutions possibles
        for digit, letters in substitutions.items():
            if digit in word:
                for letter in letters:
                    candidate = word.replace(digit, letter)
                    # Valider avec dictionnaire
                    if self.dictionary.validate(candidate.lower()):
                        candidates.append(candidate)

                    # Essayer substitutions multiples
                    for digit2, letters2 in substitutions.items():
                        if digit2 in candidate and digit2 != digit:
                            for letter2 in letters2:
                                candidate2 = candidate.replace(digit2, letter2)
                                if self.dictionary.validate(candidate2.lower()):
                                    candidates.append(candidate2)

        return list(set(candidates))

    def _find_special_chars(self, text):
        """Trouve caractères spéciaux suspects."""
        pattern = r'\b\w*[@*\[\]{}%#$^~|_=]+\w*\b'

        for match in re.finditer(pattern, text):
            word = match.group()
            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-60):min(len(text), start+60)]

            # Suggérer corrections
            suggestions = []

            # Essayer suppressions
            for char in '@*[]{}%#$^~|_=':
                if char in word:
                    candidate = word.replace(char, '')
                    if self.dictionary.validate(candidate.lower()):
                        suggestions.append(f"Supprimer '{char}' → {candidate}")

            # Essayer remplacements courants
            replacements = {
                '=': '-',
                '[': '(',
                ']': ')',
                '@': 'a',
            }
            for old, new in replacements.items():
                if old in word:
                    candidate = word.replace(old, new)
                    if self.dictionary.validate(candidate.lower()):
                        suggestions.append(f"Remplacer '{old}'→'{new}' → {candidate}")

            self.errors['caracteres_speciaux'].append({
                'word': word,
                'line': line_num,
                'context': context,
                'suggestions': suggestions,
                'position': start
            })

    def _find_merged_words(self, text):
        """Trouve mots collés (min+Maj)."""
        pattern = r'\b([a-zàâäæçèéêëìíîïòóôöùúûü]+)([A-Z][a-zàâäæçèéêëìíîïòóôöùúûü]+)\b'

        for match in re.finditer(pattern, text):
            word = match.group()
            part1 = match.group(1)
            part2 = match.group(2)

            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-60):min(len(text), start+60)]

            suggestions = []

            # Option 1: séparer
            if self.dictionary.validate(part1) and self.dictionary.validate(part2.lower()):
                suggestions.append(f"Séparer → '{part1} {part2.lower()}'")

            # Option 2: tout minuscules
            if self.dictionary.validate(word.lower()):
                suggestions.append(f"Minuscules → '{word.lower()}'")

            # Option 3: analyser caractère de jonction
            for i in range(len(part1)-2, len(part1)+1):
                seg1 = word[:i]
                seg2 = word[i:]
                if seg1 and seg2:
                    if self.dictionary.validate(seg1.lower()) and self.dictionary.validate(seg2.lower()):
                        suggestions.append(f"Séparer à pos {i} → '{seg1} {seg2}'")

            self.errors['mots_colles'].append({
                'word': word,
                'line': line_num,
                'context': context,
                'suggestions': suggestions,
                'position': start,
                'parts': (part1, part2)
            })

    def _find_letter_duplicates(self, text):
        """Trouve répétitions excessives de lettres."""
        pattern = r'\b\w*([a-zàâäæçèéêëìíîïòóôöùúûü])\1{2,}\w*\b'

        for match in re.finditer(pattern, text, re.IGNORECASE):
            word = match.group()

            # Ignorer chiffres romains
            if re.match(r'^[IVXLCDM]+$', word):
                continue

            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-60):min(len(text), start+60)]

            # Suggestions
            letter = match.group(1)
            suggestions = []

            # Essayer double
            triple_or_more = re.search(f'{letter}{{3,}}', word)
            if triple_or_more:
                candidate = word.replace(triple_or_more.group(), letter * 2)
                if self.dictionary.validate(candidate.lower()):
                    suggestions.append(f"Réduire à double → '{candidate}'")

                # Essayer simple
                candidate = word.replace(triple_or_more.group(), letter)
                if self.dictionary.validate(candidate.lower()):
                    suggestions.append(f"Réduire à simple → '{candidate}'")

            self.errors['doublons_lettres'].append({
                'word': word,
                'line': line_num,
                'context': context,
                'suggestions': suggestions,
                'position': start
            })

    def _find_weird_case(self, text):
        """Trouve casse bizarre."""
        pattern = r'\b[A-Z][a-z]*[A-Z][a-z]*[A-Z][a-zA-Z]*\b'

        for match in re.finditer(pattern, text):
            word = match.group()

            # Ignorer acronymes
            if word.isupper() and 2 <= len(word) <= 5:
                continue

            # Ignorer noms propres normaux
            if word[0].isupper() and word[1:].islower():
                continue

            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-60):min(len(text), start+60)]

            suggestions = []

            # Tout minuscules
            if self.dictionary.validate(word.lower()):
                suggestions.append(f"Minuscules → '{word.lower()}'")

            # Première maj seulement
            candidate = word[0] + word[1:].lower()
            if self.dictionary.validate(candidate.lower()):
                suggestions.append(f"Nom propre → '{candidate}'")

            self.errors['casse_bizarre'].append({
                'word': word,
                'line': line_num,
                'context': context,
                'suggestions': suggestions,
                'position': start
            })

    def _find_ligatures(self, text):
        """Trouve ligatures Unicode."""
        ligatures = {
            'Œ': 'Oe', 'œ': 'oe',
            'Æ': 'Ae', 'æ': 'ae',
            'Ÿ': 'Y',
            'ﬁ': 'fi', 'ﬂ': 'fl',
            'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl'
        }

        for lig, replacement in ligatures.items():
            for match in re.finditer(re.escape(lig), text):
                start = match.start()
                line_num = text[:start].count('\n') + 1
                context = text[max(0, start-60):min(len(text), start+60)]

                self.errors['ligatures'].append({
                    'char': lig,
                    'line': line_num,
                    'context': context,
                    'suggestions': [f"Remplacer → '{replacement}'"],
                    'position': start
                })

    def _find_weird_punctuation(self, text):
        """Trouve ponctuation bizarre."""
        # Espaces multiples
        for match in re.finditer(r'  +', text):
            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-40):min(len(text), start+40)]

            self.errors['espaces_multiples'].append({
                'count': len(match.group()),
                'line': line_num,
                'context': context,
                'suggestions': ["Réduire à un seul espace"],
                'position': start
            })

    def _find_suspicious_short_words(self, text):
        """Trouve mots courts suspects (lm, im, etc.)."""
        # Patterns connus d'erreurs OCR
        patterns = {
            r'\blm\b': 'les',
            r'\bim\b': 'il',
            r'\btm\b': 'tu',
            r'\bJf\b': 'Il',
            r'\bù\b': 'à',
            r'\bô\b': '?',
        }

        for pattern, suggestion in patterns.items():
            for match in re.finditer(pattern, text):
                start = match.start()
                line_num = text[:start].count('\n') + 1
                context = text[max(0, start-60):min(len(text), start+60)]

                self.errors['mots_courts_suspects'].append({
                    'word': match.group(),
                    'line': line_num,
                    'context': context,
                    'suggestions': [f"Probablement → '{suggestion}'"],
                    'position': start
                })

    def _find_accent_issues(self, text):
        """Trouve problèmes d'accents."""
        # ç sans voyelle après
        pattern = r'\b\w*ç(?![aouàâäèéêëìíîïòóôöùúûü])\w*\b'

        for match in re.finditer(pattern, text):
            word = match.group()
            start = match.start()
            line_num = text[:start].count('\n') + 1
            context = text[max(0, start-60):min(len(text), start+60)]

            suggestions = []

            # Essayer remplacements
            for replacement in ['c', ' ', '']:
                if replacement:
                    candidate = word.replace('ç', replacement)
                else:
                    candidate = word.replace('ç', '')

                if candidate and self.dictionary.validate(candidate.lower()):
                    suggestions.append(f"ç → '{replacement or 'supprimer'}' → {candidate}")

            self.errors['accents_suspects'].append({
                'word': word,
                'line': line_num,
                'context': context,
                'suggestions': suggestions,
                'position': start
            })

    def _find_spacing_issues(self, text):
        """Trouve problèmes d'espacement."""
        # Espace avant ponctuation faible (virgule, point)
        for match in re.finditer(r' +[,.]', text):
            start = match.start()
            line_num = text[:start].count('\n') + 1

            self.errors['espacement_ponctuation'].append({
                'error': match.group(),
                'line': line_num,
                'suggestions': ["Supprimer espace avant ponctuation"],
                'position': start
            })

    def generate_report(self):
        """Génère rapport détaillé."""
        total = sum(len(v) for v in self.errors.values())

        report = []
        report.append("=" * 80)
        report.append(f"📋 ANALYSE DÉTAILLÉE - {total} ERREURS TROUVÉES")
        report.append("=" * 80)
        report.append("")

        # Résumé
        report.append("📊 RÉSUMÉ PAR CATÉGORIE:")
        report.append("-" * 80)
        report.append("")

        sorted_cats = sorted(self.errors.items(), key=lambda x: len(x[1]), reverse=True)

        for cat, errors in sorted_cats:
            if errors:
                report.append(f"🔸 {cat.upper().replace('_', ' ')}: {len(errors)}")

        report.append("")
        report.append("=" * 80)
        report.append("📝 DÉTAILS + SUGGESTIONS PAR ERREUR")
        report.append("=" * 80)

        for cat, errors in sorted_cats:
            if not errors:
                continue

            report.append("")
            report.append(f"\n{'=' * 80}")
            report.append(f"🔸 {cat.upper().replace('_', ' ')} ({len(errors)} erreurs)")
            report.append("=" * 80)
            report.append("")

            # Trier par ligne
            errors_sorted = sorted(errors, key=lambda x: x.get('position', 0))

            for i, error in enumerate(errors_sorted, 1):
                report.append(f"\n#{i} - Ligne {error.get('line', '?')}")
                report.append("-" * 80)

                if 'word' in error:
                    report.append(f"   Erreur: '{error['word']}'")
                elif 'char' in error:
                    report.append(f"   Caractère: '{error['char']}'")
                elif 'error' in error:
                    report.append(f"   Erreur: {error['error']}")

                # Contexte
                if 'context' in error:
                    ctx = error['context'].replace('\n', ' ')
                    report.append(f"   Contexte: ...{ctx}...")

                # Suggestions
                if error.get('suggestions'):
                    report.append(f"   💡 Suggestions:")
                    for sugg in error['suggestions'][:5]:  # Max 5 suggestions
                        report.append(f"      • {sugg}")
                else:
                    report.append(f"   ⚠️  Aucune suggestion automatique")

                report.append("")

        return "\n".join(report)


def main():
    book_path = "livres_corriges/Villiers,Gérard de [SAS-047] Mission impossible en Somalie_FINAL.txt"

    if not Path(book_path).exists():
        print(f"❌ Fichier non trouvé: {book_path}")
        return

    print("=" * 80)
    print("🔍 ANALYSE DÉTAILLÉE DU FICHIER FINAL")
    print("=" * 80)
    print()
    print(f"📖 Fichier: {book_path}")

    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"📊 Taille: {len(text):,} caractères")
    print()

    analyzer = DetailedErrorAnalyzer()
    analyzer.analyze(text)

    print("✓ Analyse terminée\n")

    report = analyzer.generate_report()
    print(report)

    # Sauvegarder
    output = "ANALYSE_DETAILLEE_FINALE.txt"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n💾 Rapport détaillé sauvegardé: {output}")


if __name__ == "__main__":
    main()
