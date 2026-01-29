#!/usr/bin/env python3
"""
Auto EPUB Cleaner - Surveillance automatique du répertoire livres_originaux
Nettoie automatiquement les EPUBs et les place dans livres_traites
"""

import os
import sys
import time
from pathlib import Path
from epub_cleaner_complete import CompleteEPUBCleaner


class AutoEPUBCleaner:
    """Nettoie automatiquement les EPUBs d'un répertoire source vers un répertoire cible"""

    def __init__(self, input_dir="livres_originaux", output_dir="livres_traites"):
        """
        Initialise le nettoyeur automatique

        Args:
            input_dir: Répertoire contenant les EPUBs à nettoyer
            output_dir: Répertoire où sauvegarder les EPUBs nettoyés
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.processed_files = set()

    def setup_directories(self):
        """Crée les répertoires s'ils n'existent pas"""
        # Créer le répertoire d'entrée
        if not self.input_dir.exists():
            self.input_dir.mkdir(parents=True)
            print(f"✓ Répertoire créé: {self.input_dir}/")
            print(f"  → Placez vos fichiers EPUB à nettoyer dans ce répertoire\n")

        # Créer le répertoire de sortie
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)
            print(f"✓ Répertoire créé: {self.output_dir}/")
            print(f"  → Les fichiers nettoyés seront sauvegardés ici\n")

    def get_epub_files(self):
        """Récupère la liste des fichiers EPUB à traiter"""
        if not self.input_dir.exists():
            return []

        # Trouver tous les fichiers .epub
        epub_files = list(self.input_dir.glob("*.epub"))

        # Filtrer les fichiers déjà traités
        new_files = [f for f in epub_files if f not in self.processed_files]

        return new_files

    def clean_single_file(self, input_path):
        """
        Nettoie un seul fichier EPUB

        Args:
            input_path: Chemin vers le fichier EPUB à nettoyer

        Returns:
            bool: True si le nettoyage a réussi, False sinon
        """
        filename = input_path.name
        output_path = self.output_dir / filename

        print(f"📖 Traitement: {filename}")

        try:
            cleaner = CompleteEPUBCleaner(str(input_path))

            # Nettoyer le fichier (Parallel Mode)
            success = cleaner.clean(str(output_path), max_workers=2)

            if success:
                print(f"✓ Sauvegardé: {output_path}\n")
                self.processed_files.add(input_path)
                return True
            else:
                print(f"✗ Échec du nettoyage de {filename}\n")
                return False

        except Exception as e:
            print(f"✗ Erreur lors du traitement de {filename}: {e}\n")
            return False

    def clean_all(self):
        """Nettoie tous les fichiers EPUB du répertoire d'entrée"""
        # S'assurer que les répertoires existent
        self.setup_directories()

        # Récupérer les fichiers à traiter
        epub_files = self.get_epub_files()

        if not epub_files:
            print(f"ℹ️  Aucun nouveau fichier EPUB dans {self.input_dir}/")
            return 0, 0

        print(f"📚 {len(epub_files)} fichier(s) EPUB à nettoyer\n")
        print("=" * 80)

        # Statistiques
        success_count = 0
        failed_count = 0

        # Traiter chaque fichier
        for i, epub_file in enumerate(epub_files, 1):
            print(f"[{i}/{len(epub_files)}]")

            if self.clean_single_file(epub_file):
                success_count += 1
            else:
                failed_count += 1

            print("-" * 80)

        return success_count, failed_count

    def watch_mode(self, interval=10):
        """
        Mode surveillance: surveille continuellement le répertoire d'entrée

        Args:
            interval: Intervalle de vérification en secondes
        """
        print("=" * 80)
        print("👁️  MODE SURVEILLANCE ACTIVÉ")
        print("=" * 80)
        print(f"Surveillance du répertoire: {self.input_dir}/")
        print(f"Intervalle de vérification: {interval} secondes")
        print("Appuyez sur Ctrl+C pour arrêter\n")

        self.setup_directories()

        try:
            while True:
                epub_files = self.get_epub_files()

                if epub_files:
                    print(f"\n📚 {len(epub_files)} nouveau(x) fichier(s) détecté(s)")
                    print("=" * 80)

                    for epub_file in epub_files:
                        self.clean_single_file(epub_file)

                    print("✓ Traitement terminé. En attente de nouveaux fichiers...\n")
                else:
                    # Afficher un point pour montrer que le programme fonctionne
                    print(".", end="", flush=True)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⛔ Surveillance arrêtée par l'utilisateur")


def print_usage():
    """Affiche l'aide d'utilisation"""
    print("=" * 80)
    print("📚 AUTO EPUB CLEANER")
    print("=" * 80)
    print("\nUsage:")
    print("  python auto_cleaner.py [options]\n")
    print("Options:")
    print("  (aucune)         Nettoie tous les EPUBs de livres_originaux/")
    print("  --watch          Mode surveillance (vérifie continuellement)")
    print("  --interval N     Intervalle de vérification en secondes (défaut: 10)")
    print("  --input DIR      Répertoire d'entrée personnalisé")
    print("  --output DIR     Répertoire de sortie personnalisé")
    print("  --help           Affiche cette aide\n")
    print("Exemples:")
    print("  # Nettoyer tous les fichiers une fois")
    print("  python auto_cleaner.py\n")
    print("  # Mode surveillance avec intervalle de 30 secondes")
    print("  python auto_cleaner.py --watch --interval 30\n")
    print("  # Répertoires personnalisés")
    print("  python auto_cleaner.py --input mes_livres --output livres_propres\n")
    print("Structure des répertoires:")
    print("  livres_originaux/    ← Placez vos EPUBs ici")
    print("  livres_traites/      ← Les EPUBs nettoyés seront ici")
    print("=" * 80)


def main():
    """Fonction principale"""
    # Paramètres par défaut
    input_dir = "livres_originaux"
    output_dir = "livres_traites"
    watch_mode = False
    interval = 10

    # Parser les arguments
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)

    # Parser les arguments personnalisés
    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--watch":
            watch_mode = True
            i += 1
        elif arg == "--interval" and i + 1 < len(args):
            try:
                interval = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"✗ Erreur: --interval doit être un nombre entier")
                sys.exit(1)
        elif arg == "--input" and i + 1 < len(args):
            input_dir = args[i + 1]
            i += 2
        elif arg == "--output" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            print(f"✗ Argument inconnu: {arg}")
            print("Utilisez --help pour voir l'aide")
            sys.exit(1)

    # Créer le nettoyeur automatique
    cleaner = AutoEPUBCleaner(input_dir, output_dir)

    # Mode surveillance ou nettoyage unique
    if watch_mode:
        cleaner.watch_mode(interval)
    else:
        print("=" * 80)
        print("📚 AUTO EPUB CLEANER")
        print("=" * 80)
        print(f"Répertoire d'entrée: {input_dir}/")
        print(f"Répertoire de sortie: {output_dir}/")
        print("=" * 80)
        print()

        success, failed = cleaner.clean_all()

        # Afficher le résumé
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ")
        print("=" * 80)
        print(f"✓ Fichiers nettoyés avec succès: {success}")
        print(f"✗ Fichiers en échec: {failed}")
        print("=" * 80)

        if success == 0 and failed == 0:
            print(f"\nℹ️  Conseil: Placez vos fichiers EPUB dans {input_dir}/")
            print(f"   puis relancez: python auto_cleaner.py")


if __name__ == "__main__":
    main()
