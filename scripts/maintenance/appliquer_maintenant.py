#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applique les validations IMMÉDIATEMENT (sans confirmation interactive)
À utiliser quand l'utilisateur a explicitement demandé l'application
"""

import csv
import shutil
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
                    inversions_approuvees.append(row)

    except Exception as e:
        print(f"   ⚠️  Erreur lecture {Path(fichier_validation).name}: {e}")
        return [], []

    return inversions_approuvees, inversions_rejetees


def appliquer_inversions(fichier_base: str, inversions_approuvees: list, backup: bool = True):
    """Applique les inversions validées au fichier validation_humaine.csv"""

    # Créer un index des inversions par nom de fichier
    inversions_index = {}
    for inv in inversions_approuvees:
        fichier = inv['Fichier']
        inversions_index[fichier] = {
            'titre_actuel': inv['Titre_actuel'],
            'auteur_actuel': inv['Auteur_actuel'],
            'titre_corrige': inv.get('Titre_corrigé', inv['Auteur_actuel']),
            'auteur_corrige': inv.get('Auteur_corrigé', inv['Titre_actuel'])
        }

    # Backup du fichier original
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fichier_backup = fichier_base.replace('.csv', f'_backup_{timestamp}.csv')
        shutil.copy2(fichier_base, fichier_backup)
        print(f"📦 Backup créé : {Path(fichier_backup).name}")
        print()

    # Lire et modifier le fichier base
    lignes_modifiees = []
    compteur_modif = 0

    with open(fichier_base, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames

        for row in reader:
            fichier = row.get('Fichier', '')

            # Si ce fichier doit être inversé
            if fichier in inversions_index:
                inv = inversions_index[fichier]

                # Vérifier que les valeurs actuelles correspondent
                if (row['Titre'] == inv['titre_actuel'] and
                    row['Auteur(s)'] == inv['auteur_actuel']):

                    # Appliquer l'inversion
                    row['Titre'] = inv['titre_corrige']
                    row['Auteur(s)'] = inv['auteur_corrige']
                    compteur_modif += 1

            lignes_modifiees.append(row)

    # Écrire le fichier de sortie
    with open(fichier_base, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(lignes_modifiees)

    return compteur_modif


def main():
    """Applique IMMÉDIATEMENT les validations"""

    dossier_validation = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_amelioree"
    fichier_base = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_humaine.csv"

    print("=" * 80)
    print("APPLICATION DES VALIDATIONS - MISE À JOUR BASE DE DONNÉES")
    print("=" * 80)
    print()

    # Trouver tous les fichiers CSV de validation
    fichiers_validation = list(Path(dossier_validation).glob("validation_*.csv"))

    if not fichiers_validation:
        print(f"❌ Aucun fichier de validation CSV trouvé")
        return

    print(f"📁 Dossier : validation_amelioree/")
    print(f"📄 {len(fichiers_validation)} fichiers CSV trouvés")
    print()
    print("=" * 80)
    print("LECTURE DES VALIDATIONS")
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
        print()

    # Résumé
    print("=" * 80)
    print("RÉSUMÉ DES VALIDATIONS")
    print("=" * 80)
    print(f"Total inversions approuvées : {len(toutes_inversions_approuvees)}")
    print(f"Total inversions rejetées   : {len(toutes_inversions_rejetees)}")
    print()

    if len(toutes_inversions_approuvees) == 0:
        print("⚠️  Aucune inversion approuvée à appliquer.")
        return

    # Appliquer les inversions (sans demander confirmation)
    print("=" * 80)
    print("APPLICATION DES INVERSIONS")
    print("=" * 80)
    print()

    nb_modif = appliquer_inversions(fichier_base, toutes_inversions_approuvees)

    print("=" * 80)
    print("✅ MODIFICATIONS APPLIQUÉES AVEC SUCCÈS")
    print("=" * 80)
    print(f"Nombre de lignes modifiées : {nb_modif}")
    print(f"Fichier mis à jour : validation_humaine.csv")
    print()

    # Générer un rapport
    rapport_fichier = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/rapport_corrections_amelioree.txt"

    with open(rapport_fichier, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RAPPORT DE CORRECTIONS APPLIQUÉES - MÉTHODE AMÉLIORÉE\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nDate : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\nInversions approuvées : {len(toutes_inversions_approuvees)}\n")
        f.write(f"Inversions rejetées : {len(toutes_inversions_rejetees)}\n")
        f.write(f"Modifications appliquées : {nb_modif}\n")
        f.write("\n" + "=" * 80 + "\n")
        f.write("INVERSIONS APPLIQUÉES\n")
        f.write("=" * 80 + "\n\n")

        for inv in toutes_inversions_approuvees:
            f.write(f"📁 {inv['Fichier']}\n")
            f.write(f"   AVANT : Titre={inv['Titre_actuel']} | Auteur={inv['Auteur_actuel']}\n")
            titre_corrige = inv.get('Titre_corrigé', inv['Auteur_actuel'])
            auteur_corrige = inv.get('Auteur_corrigé', inv['Titre_actuel'])
            f.write(f"   APRÈS : Titre={titre_corrige} | Auteur={auteur_corrige}\n")
            f.write(f"   Score={inv.get('Score', 'N/A')}\n\n")

        if toutes_inversions_rejetees:
            f.write("\n" + "=" * 80 + "\n")
            f.write("INVERSIONS REJETÉES (faux positifs)\n")
            f.write("=" * 80 + "\n\n")

            for inv in toutes_inversions_rejetees:
                f.write(f"📁 {inv['Fichier']}\n")
                f.write(f"   Titre={inv['Titre_actuel']} | Auteur={inv['Auteur_actuel']}\n")
                f.write(f"   Score={inv.get('Score', 'N/A')} | Action={inv['ACTION']}\n\n")

    print(f"📄 Rapport détaillé sauvegardé : {Path(rapport_fichier).name}")
    print()
    print("=" * 80)
    print("🎉 MISE À JOUR TERMINÉE !")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
