#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier les validations
Mode DRY-RUN : ne modifie rien, affiche juste ce qui serait fait
"""

import csv
from pathlib import Path
from datetime import datetime


def lire_inversions_validees(fichier_validation: str):
    """Lit un fichier de validation et retourne les inversions approuvées"""

    inversions_approuvees = []
    inversions_rejetees = []

    try:
        with open(fichier_validation, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                # Ignorer les lignes d'instructions
                if row.get('ID') == '→':
                    continue

                # Vérifier que les colonnes essentielles existent
                if not all(k in row for k in ['Fichier', 'Titre_actuel', 'Auteur_actuel']):
                    continue

                action = row.get('ACTION', '').strip().upper()

                # Déterminer si l'inversion est approuvée ou rejetée
                if action in ['X', 'NON', 'FAUX', 'NO', 'N', 'REJECT']:
                    inversions_rejetees.append(row)
                else:
                    # Vide, 'OK', 'OUI', ou autre = approuvé
                    inversions_approuvees.append(row)

    except Exception as e:
        print(f"   ⚠️  Erreur lecture {Path(fichier_validation).name}: {e}")
        return [], []

    return inversions_approuvees, inversions_rejetees


def main():
    """Test en mode DRY-RUN (lecture seule)"""

    dossier_validation = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_amelioree"

    print("=" * 80)
    print("TEST DES VALIDATIONS - MODE DRY-RUN")
    print("(Aucune modification ne sera effectuée)")
    print("=" * 80)
    print()

    # Trouver tous les fichiers CSV de validation
    fichiers_validation = list(Path(dossier_validation).glob("validation_*.csv"))

    if not fichiers_validation:
        print(f"❌ Aucun fichier de validation CSV trouvé")
        return

    # Vérifier si des fichiers .numbers existent
    fichiers_numbers = list(Path(dossier_validation).glob("*.numbers"))
    if fichiers_numbers:
        print(f"📊 {len(fichiers_numbers)} fichiers .numbers détectés :")
        for f in sorted(fichiers_numbers):
            print(f"   • {f.name}")
        print()

    print(f"📁 Dossier : validation_amelioree/")
    print(f"📄 {len(fichiers_validation)} fichiers CSV trouvés")
    print()
    print("=" * 80)
    print("ANALYSE DES VALIDATIONS")
    print("=" * 80)
    print()

    # Collecter toutes les inversions
    toutes_inversions_approuvees = []
    toutes_inversions_rejetees = []

    for fichier in sorted(fichiers_validation):
        print(f"📄 {fichier.name}...")

        approuvees, rejetees = lire_inversions_validees(str(fichier))

        toutes_inversions_approuvees.extend(approuvees)
        toutes_inversions_rejetees.extend(rejetees)

        print(f"   ✅ {len(approuvees)} inversions approuvées")
        print(f"   ❌ {len(rejetees)} inversions rejetées")

        # Afficher quelques exemples de rejets
        if rejetees:
            print(f"   📝 Exemples de rejets :")
            for rej in rejetees[:3]:
                print(f"      • {rej['Fichier'][:60]}...")
        print()

    # Résumé
    print("=" * 80)
    print("RÉSUMÉ DES VALIDATIONS")
    print("=" * 80)
    print(f"Total inversions approuvées : {len(toutes_inversions_approuvees)}")
    print(f"Total inversions rejetées   : {len(toutes_inversions_rejetees)}")
    print()

    if len(toutes_inversions_rejetees) > 0:
        print("=" * 80)
        print(f"DÉTAIL DES {len(toutes_inversions_rejetees)} INVERSIONS REJETÉES")
        print("=" * 80)
        print()

        for inv in toutes_inversions_rejetees:
            print(f"📁 {inv['Fichier']}")
            print(f"   Titre actuel  : {inv['Titre_actuel']}")
            print(f"   Auteur actuel : {inv['Auteur_actuel']}")
            print(f"   Score         : {inv.get('Score', 'N/A')}")
            print(f"   ACTION        : {inv['ACTION']}")
            print(f"   → Sera conservé TEL QUEL (pas d'inversion)")
            print()

    if len(toutes_inversions_approuvees) > 0:
        print("=" * 80)
        print(f"APERÇU DES INVERSIONS QUI SERONT APPLIQUÉES")
        print("=" * 80)
        print()
        print("(Affichage des 10 premières)")
        print()

        for inv in toutes_inversions_approuvees[:10]:
            print(f"📁 {inv['Fichier']}")
            print(f"   ❌ AVANT : Titre=\"{inv['Titre_actuel']}\" | Auteur=\"{inv['Auteur_actuel']}\"")
            titre_corrige = inv.get('Titre_corrigé', inv['Auteur_actuel'])
            auteur_corrige = inv.get('Auteur_corrigé', inv['Titre_actuel'])
            print(f"   ✅ APRÈS : Titre=\"{titre_corrige}\" | Auteur=\"{auteur_corrige}\"")
            print(f"   📊 Score={inv.get('Score', 'N/A')}")
            print()

    print("=" * 80)
    print("MODE DRY-RUN - AUCUNE MODIFICATION EFFECTUÉE")
    print("=" * 80)
    print()
    print("Pour appliquer réellement ces modifications :")
    print("   python3 appliquer_validations.py")
    print()


if __name__ == "__main__":
    main()
