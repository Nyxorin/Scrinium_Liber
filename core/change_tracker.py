#!/usr/bin/env python3
"""
Système de suivi des changements pour les corrections OCR.
Permet de générer des rapports détaillés pour l'utilisateur.
"""

from typing import List, Dict, Tuple
from collections import defaultdict
import re


class ChangeTracker:
    """Suit tous les changements effectués lors de la correction."""

    def __init__(self):
        self.changes: List[Dict] = []
        self.stats_by_rule = defaultdict(lambda: {'count': 0, 'examples': []})

    def record_change(self, rule_name: str, original: str, corrected: str,
                      context: str = "", line_num: int = 0):
        """
        Enregistre un changement.

        Args:
            rule_name: Nom de la règle qui a fait le changement
            original: Texte original
            corrected: Texte corrigé
            context: Contexte autour du changement
            line_num: Numéro de ligne
        """
        change = {
            'rule': rule_name,
            'original': original,
            'corrected': corrected,
            'context': context,
            'line': line_num
        }

        self.changes.append(change)

        # Statistiques par règle
        self.stats_by_rule[rule_name]['count'] += 1

        # Garder quelques exemples (max 10 par règle)
        examples = self.stats_by_rule[rule_name]['examples']
        if len(examples) < 10:
            examples.append({
                'original': original,
                'corrected': corrected,
                'context': context,
                'line': line_num
            })

    def get_total_changes(self) -> int:
        """Retourne le nombre total de changements."""
        return len(self.changes)

    def get_stats(self) -> Dict:
        """Retourne les statistiques par règle."""
        return dict(self.stats_by_rule)

    def generate_report(self) -> str:
        """Génère un rapport textuel détaillé."""
        if not self.changes:
            return "Aucun changement effectué."

        report = []
        report.append("=" * 80)
        report.append(f"📊 RAPPORT DES CORRECTIONS - {self.get_total_changes()} changements")
        report.append("=" * 80)
        report.append("")

        # Statistiques par règle
        report.append("📈 STATISTIQUES PAR RÈGLE:")
        report.append("-" * 80)
        report.append("")

        sorted_rules = sorted(
            self.stats_by_rule.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        for rule_name, stats in sorted_rules:
            count = stats['count']
            report.append(f"🔹 {rule_name}: {count} correction(s)")

        report.append("")
        report.append("=" * 80)
        report.append("📝 EXEMPLES DE CORRECTIONS PAR RÈGLE:")
        report.append("=" * 80)
        report.append("")

        # Exemples par règle
        for rule_name, stats in sorted_rules:
            count = stats['count']
            examples = stats['examples']

            report.append(f"\n🔹 {rule_name.upper()} ({count} total)")
            report.append("-" * 80)

            if examples:
                for i, ex in enumerate(examples[:10], 1):
                    report.append(f"\n  Exemple {i}:")
                    report.append(f"    AVANT: {ex['original']}")
                    report.append(f"    APRÈS: {ex['corrected']}")
                    if ex['context']:
                        ctx = ex['context'].replace('\n', ' ')[:100]
                        report.append(f"    Contexte: ...{ctx}...")
                    if ex['line']:
                        report.append(f"    Ligne: {ex['line']}")

                if count > 10:
                    report.append(f"\n    ... et {count - 10} autres corrections similaires")

            report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def save_detailed_report(self, filepath: str):
        """Sauvegarde un rapport détaillé dans un fichier."""
        with open(filepath, 'w', encoding='utf-8') as f:
            # En-tête
            f.write("=" * 80 + "\n")
            f.write(f"RAPPORT DÉTAILLÉ DES CORRECTIONS - {self.get_total_changes()} changements\n")
            f.write("=" * 80 + "\n\n")

            # Résumé par règle
            f.write("RÉSUMÉ PAR RÈGLE:\n")
            f.write("-" * 80 + "\n")

            sorted_rules = sorted(
                self.stats_by_rule.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )

            for rule_name, stats in sorted_rules:
                f.write(f"\n{rule_name}: {stats['count']} correction(s)\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("LISTE COMPLÈTE DES CHANGEMENTS:\n")
            f.write("=" * 80 + "\n\n")

            # Tous les changements, groupés par règle
            for rule_name, stats in sorted_rules:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"{rule_name.upper()} - {stats['count']} correction(s)\n")
                f.write(f"{'=' * 80}\n\n")

                # Filtrer les changements pour cette règle
                rule_changes = [c for c in self.changes if c['rule'] == rule_name]

                for i, change in enumerate(rule_changes, 1):
                    f.write(f"{i}. AVANT: {change['original']}\n")
                    f.write(f"   APRÈS: {change['corrected']}\n")
                    if change['context']:
                        ctx = change['context'].replace('\n', ' ')
                        f.write(f"   Contexte: {ctx}\n")
                    if change['line']:
                        f.write(f"   Ligne: {change['line']}\n")
                    f.write("\n")

    def get_summary(self) -> str:
        """Retourne un résumé court."""
        if not self.changes:
            return "Aucun changement."

        total = self.get_total_changes()
        num_rules = len(self.stats_by_rule)

        return f"{total} changements effectués par {num_rules} règle(s)"


class TrackedCorrector:
    """
    Wrapper pour appliquer des corrections avec suivi automatique.
    """

    def __init__(self, tracker: ChangeTracker):
        self.tracker = tracker

    def apply_replacement(self, text: str, pattern: str, replacement: str,
                         rule_name: str, is_regex: bool = True) -> str:
        """
        Applique un remplacement avec suivi automatique.

        Args:
            text: Texte à corriger
            pattern: Pattern à chercher (regex ou string)
            replacement: Remplacement
            rule_name: Nom de la règle pour le tracking
            is_regex: Si True, utilise regex, sinon remplacement simple

        Returns:
            Texte corrigé
        """
        if is_regex:
            # Regex avec suivi
            def replace_func(match):
                original = match.group(0)
                # Appliquer le remplacement
                corrected = re.sub(pattern, replacement, original)

                if original != corrected:
                    # Trouver contexte
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    # Ligne approximative
                    line_num = text[:match.start()].count('\n') + 1

                    self.tracker.record_change(
                        rule_name=rule_name,
                        original=original,
                        corrected=corrected,
                        context=context,
                        line_num=line_num
                    )

                return corrected

            return re.sub(pattern, replace_func, text)

        else:
            # Remplacement simple avec suivi
            count = text.count(pattern)
            if count > 0:
                # Trouver toutes les occurrences pour le contexte
                pos = 0
                while True:
                    pos = text.find(pattern, pos)
                    if pos == -1:
                        break

                    # Contexte
                    start = max(0, pos - 50)
                    end = min(len(text), pos + len(pattern) + 50)
                    context = text[start:end]

                    # Ligne
                    line_num = text[:pos].count('\n') + 1

                    self.tracker.record_change(
                        rule_name=rule_name,
                        original=pattern,
                        corrected=replacement,
                        context=context,
                        line_num=line_num
                    )

                    pos += len(pattern)

                text = text.replace(pattern, replacement)

            return text
