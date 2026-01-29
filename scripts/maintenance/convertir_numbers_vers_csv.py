#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertit les fichiers Numbers en CSV pour la validation
Utilise AppleScript pour exporter depuis Numbers
"""

import subprocess
import os
from pathlib import Path


def convertir_numbers_vers_csv(fichier_numbers: str) -> str:
    """
    Convertit un fichier .numbers en CSV en utilisant AppleScript

    Retourne le chemin du fichier CSV créé
    """

    fichier_numbers_path = Path(fichier_numbers).resolve()
    fichier_csv = str(fichier_numbers_path).replace('.numbers', '.csv')

    # Script AppleScript pour exporter Numbers vers CSV
    applescript = f'''
    tell application "Numbers"
        set theDoc to open POSIX file "{fichier_numbers_path}"

        -- Exporter en CSV
        export theDoc to POSIX file "{fichier_csv}" as CSV

        -- Fermer sans sauvegarder
        close theDoc saving no
    end tell
    '''

    try:
        # Exécuter le script AppleScript
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"   ✅ Converti : {Path(fichier_numbers).name}")
            return fichier_csv
        else:
            print(f"   ❌ Erreur : {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout lors de la conversion de {Path(fichier_numbers).name}")
        return None
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return None


def convertir_tous_les_numbers(dossier: str):
    """
    Convertit tous les fichiers .numbers d'un dossier en CSV
    """

    dossier_path = Path(dossier)

    if not dossier_path.exists():
        print(f"❌ Dossier non trouvé : {dossier}")
        return []

    # Trouver tous les fichiers .numbers
    fichiers_numbers = list(dossier_path.glob("*.numbers"))

    if not fichiers_numbers:
        print(f"ℹ️  Aucun fichier .numbers trouvé dans {dossier}")
        return []

    print("=" * 80)
    print("CONVERSION NUMBERS → CSV")
    print("=" * 80)
    print()
    print(f"📁 Dossier : {dossier}")
    print(f"📊 {len(fichiers_numbers)} fichiers .numbers trouvés")
    print()

    fichiers_csv_crees = []

    for fichier in sorted(fichiers_numbers):
        print(f"🔄 Conversion de {fichier.name}...")
        fichier_csv = convertir_numbers_vers_csv(str(fichier))

        if fichier_csv:
            fichiers_csv_crees.append(fichier_csv)

    print()
    print("=" * 80)
    print(f"✅ {len(fichiers_csv_crees)} fichiers convertis avec succès")
    print("=" * 80)
    print()

    return fichiers_csv_crees


def main():
    """Fonction principale"""

    # Dossier contenant les fichiers de validation
    dossier_validation = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_amelioree"

    # Convertir tous les fichiers .numbers en CSV
    fichiers_csv = convertir_tous_les_numbers(dossier_validation)

    if fichiers_csv:
        print("📝 Fichiers CSV créés :")
        for csv in fichiers_csv:
            print(f"   • {Path(csv).name}")
        print()
        print("✅ Vous pouvez maintenant exécuter :")
        print("   python3 appliquer_inversions_validees_amelioree.py")
    else:
        print("ℹ️  Aucune conversion effectuée.")
        print("   Si vous avez modifié des fichiers avec Numbers, ils sont maintenant sauvegardés.")


if __name__ == "__main__":
    main()
