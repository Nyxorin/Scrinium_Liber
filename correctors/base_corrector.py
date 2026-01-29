#!/usr/bin/env python3
"""
Classe de base abstraite pour tous les correcteurs.
Principe Odoo: Spécialisation par héritage.

Tous les correcteurs héritent de cette classe et implémentent:
- correct(): Correction du texte
- get_confidence(): Score de confiance
- get_suggestions(): Liste de suggestions alternatives
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CorrectionSuggestion:
    """
    Représente une suggestion de correction.
    """
    original: str
    corrected: str
    confidence: float
    reason: str
    alternatives: List[str] = None

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class BaseCorrector(ABC):
    """
    Classe de base abstraite pour tous les correcteurs OCR.

    Principe Odoo:
    - Base commune solide
    - Spécialisation par héritage
    - Interface uniforme

    Chaque correcteur doit implémenter:
    - correct(): Applique les corrections
    - get_confidence(): Retourne le niveau de confiance
    - get_name(): Nom du correcteur
    """

    def __init__(self, name: str = "BaseCorrector"):
        self.name = name
        self.corrections_count = 0
        self.suggestions_made: List[CorrectionSuggestion] = []

    @abstractmethod
    def correct(self, text: str) -> str:
        """
        Corrige le texte.

        Args:
            text: Texte à corriger

        Returns:
            Texte corrigé
        """
        pass

    @abstractmethod
    def get_confidence(self) -> float:
        """
        Retourne le niveau de confiance de ce correcteur.

        Returns:
            Score entre 0.0 et 1.0
            - 1.0 = 100% fiable (règles déterministes)
            - 0.9-0.95 = Très fiable (dictionnaire validé)
            - 0.7-0.9 = Fiable (transformers, grammaire)
            - 0.5-0.7 = Incertain (LLM)
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Retourne le nom du correcteur.

        Returns:
            Nom descriptif
        """
        pass

    def get_suggestions(self, text: str, max_suggestions: int = 5) -> List[CorrectionSuggestion]:
        """
        Génère des suggestions de correction (optionnel).

        Args:
            text: Texte à analyser
            max_suggestions: Nombre maximum de suggestions

        Returns:
            Liste de suggestions
        """
        # Implémentation par défaut: vide
        # Les correcteurs peuvent surcharger cette méthode
        return []

    def reset_stats(self):
        """Réinitialise les statistiques"""
        self.corrections_count = 0
        self.suggestions_made = []

    def get_stats(self) -> dict:
        """
        Retourne les statistiques du correcteur.

        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            'name': self.get_name(),
            'corrections_count': self.corrections_count,
            'suggestions_count': len(self.suggestions_made),
            'confidence': self.get_confidence()
        }

    def print_stats(self):
        """Affiche les statistiques"""
        stats = self.get_stats()
        print(f"\n{'=' * 80}")
        print(f"📊 {stats['name']} - Statistiques")
        print(f"{'=' * 80}")
        print(f"✓ Corrections appliquées: {stats['corrections_count']}")
        print(f"✓ Suggestions générées: {stats['suggestions_count']}")
        print(f"✓ Confiance: {stats['confidence'] * 100:.1f}%")
        print(f"{'=' * 80}")

    def __repr__(self):
        return f"<{self.get_name()} (confiance: {self.get_confidence():.2f})>"


class CorrectionPipeline:
    """
    Pipeline de correcteurs.
    Principe Odoo: Orchestration des modules.

    Permet de chaîner plusieurs correcteurs dans l'ordre:
    1. Déterministe (confiance 100%)
    2. Dictionnaire (confiance 100%)
    3. Transformers (confiance 90%)
    4. Grammaire (confiance 90%)
    5. LLM (confiance 80%)
    6. Humain (confiance 100%)
    """

    def __init__(self):
        self.correctors: List[BaseCorrector] = []

    def add_corrector(self, corrector: BaseCorrector):
        """Ajoute un correcteur au pipeline"""
        self.correctors.append(corrector)

    def remove_corrector(self, name: str):
        """Retire un correcteur par son nom"""
        self.correctors = [c for c in self.correctors if c.get_name() != name]

    def process(self, text: str, verbose: bool = False) -> Tuple[str, List[dict]]:
        """
        Traite le texte avec tous les correcteurs dans l'ordre.

        Args:
            text: Texte à corriger
            verbose: Afficher les détails

        Returns:
            Tuple (texte_corrigé, liste_stats_par_correcteur)
        """
        current_text = text
        all_stats = []

        for corrector in self.correctors:
            if verbose:
                print(f"\n🔧 Application de {corrector.get_name()}...")

            # Appliquer le correcteur
            corrected_text = corrector.correct(current_text)

            # Statistiques
            stats = corrector.get_stats()
            all_stats.append(stats)

            if verbose:
                print(f"   ✓ {stats['corrections_count']} corrections")

            current_text = corrected_text

        return current_text, all_stats

    def get_total_stats(self) -> dict:
        """Statistiques totales du pipeline"""
        total_corrections = sum(c.corrections_count for c in self.correctors)

        return {
            'correctors_count': len(self.correctors),
            'total_corrections': total_corrections,
            'correctors': [c.get_stats() for c in self.correctors]
        }

    def print_stats(self):
        """Affiche les statistiques complètes"""
        stats = self.get_total_stats()

        print(f"\n{'=' * 80}")
        print(f"📊 PIPELINE DE CORRECTION - Statistiques Globales")
        print(f"{'=' * 80}")
        print(f"✓ Nombre de correcteurs: {stats['correctors_count']}")
        print(f"✓ Total corrections: {stats['total_corrections']}")
        print()

        for corrector_stats in stats['correctors']:
            print(f"  📌 {corrector_stats['name']}: "
                  f"{corrector_stats['corrections_count']} corrections "
                  f"(confiance: {corrector_stats['confidence'] * 100:.0f}%)")

        print(f"{'=' * 80}")


if __name__ == "__main__":
    # Test avec un correcteur fictif
    class TestCorrector(BaseCorrector):
        def __init__(self):
            super().__init__()

        def correct(self, text: str) -> str:
            # Simple test: remplace "test" par "TEST"
            corrected = text.replace("test", "TEST")
            if corrected != text:
                self.corrections_count += 1
            return corrected

        def get_confidence(self) -> float:
            return 1.0  # 100% confiance

        def get_name(self) -> str:
            return "TestCorrector"

    # Test
    print("🧪 Test de BaseCorrector:")
    corrector = TestCorrector()
    text = "Ceci est un test de test."
    corrected = corrector.correct(text)

    print(f"\nOriginal: {text}")
    print(f"Corrigé: {corrected}")
    corrector.print_stats()
