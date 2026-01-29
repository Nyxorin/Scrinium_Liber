#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applique les inversions validées par l'utilisateur
VERSION SIMPLIFIÉE pour Numbers

WORKFLOW :
1. Lit les CSV de validation du dossier validation_amelioree/
2. Analyse la colonne ACTION (vide = accepter, X = rejeter)
3. Crée un backup de validation_humaine.csv
4. Applique les inversions approuvées

IMPORTANT : Si vous avez modifié les fichiers avec Numbers,
n'oubliez pas de les EXPORTER EN CSV avant d'exécuter ce script !
(Fichier → Exporter vers → CSV, avec séparateur point-virgule)
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime


def lire_inversions_validees(fichier_validation: str):
    """
    Lit un fichier de validation et retourne les inversions approuvées

    La colonne ACTION détermine l'action :
    - Vide ou "OK" → Accepter l'inversion
    - "X", "NON", "FAUX" → Rejeter l'inversion
    """

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


def appliquer_inversions(fichier_base: str, inversions_approuvees: list, backup: bool = True):
    """
    Applique les inversions validées au fichier validation_humaine.csv
    """

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
    """
    Traite les fichiers de validation de la méthode améliorée
    """

    dossier_validation = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_amelioree"
    fichier_base = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_humaine.csv"

    # Vérifier que le dossier existe
    if not Path(dossier_validation).exists():
        print(f"❌ Dossier de validation non trouvé : {dossier_validation}")
        print(f"   Exécutez d'abord : python3 generer_validation_methode_amelioree.py")
        return

    print("=" * 80)
    print("APPLICATION DES VALIDATIONS - MÉTHODE AMÉLIORÉE")
    print("=" * 80)
    print()

    # Trouver tous les fichiers CSV de validation
    fichiers_validation = list(Path(dossier_validation).glob("validation_*.csv"))

    if not fichiers_validation:
        print(f"❌ Aucun fichier de validation CSV trouvé dans {dossier_validation}")
        print()
        print("💡 Si vous avez modifié des fichiers avec Numbers :")
        print("   1. Ouvrez le fichier .numbers")
        print("   2. Fichier → Exporter vers → CSV")
        print("   3. Séparateur : Point-virgule")
        print("   4. Encodage : UTF-8")
        print("   5. Enregistrez en écrasant le fichier CSV original")
        return

    # Vérifier si des fichiers .numbers existent
    fichiers_numbers = list(Path(dossier_validation).glob("*.numbers"))
    if fichiers_numbers:
        print("⚠️  ATTENTION : Fichiers .numbers détectés !")
        print()
        print(f"   {len(fichiers_numbers)} fichiers .numbers trouvés :")
        for f in sorted(fichiers_numbers):
            print(f"   • {f.name}")
        print()
        print("💡 N'oubliez pas d'exporter ces fichiers en CSV depuis Numbers :")
        print("   Fichier → Exporter vers → CSV (séparateur point-virgule)")
        print()
        reponse = input("Avez-vous déjà exporté tous vos fichiers en CSV ? [o/N] : ")
        if reponse.lower() not in ['o', 'oui', 'y', 'yes']:
            print()
            print("❌ Merci d'exporter d'abord vos fichiers .numbers en CSV.")
            print("   Puis relancez ce script.")
            return
        print()

    print(f"📁 Dossier : validation_amelioree/")
    print(f"📊 {len(fichiers_validation)} fichiers CSV de validation trouvés")
    print()
    print("=" * 80)
    print("LECTURE DES VALIDATIONS")
    print("=" * 80)
    print()

    # Collecter toutes les inversions approuvées
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
        print()
        print("💡 Conseil : Ouvrez les fichiers CSV avec Numbers, remplissez la colonne ACTION :")
        print("   • Laissez VIDE pour accepter l'inversion")
        print("   • Écrivez X pour rejeter l'inversion")
        print()
        print("   Puis exportez en CSV : Fichier → Exporter vers → CSV (point-virgule)")
        return

    # Demander confirmation
    print("⚠️  ATTENTION : Cette opération va modifier validation_humaine.csv")
    print("   Un backup sera créé automatiquement.")
    print()
    reponse = input("Voulez-vous continuer ? [o/N] : ")

    if reponse.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Opération annulée.")
        return

    # Appliquer les inversions
    print()
    print("=" * 80)
    print("APPLICATION DES INVERSIONS")
    print("=" * 80)
    print()

    nb_modif = appliquer_inversions(fichier_base, toutes_inversions_approuvees)

    print()
    print("=" * 80)
    print("✅ MODIFICATIONS APPLIQUÉES")
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

    print(f"📄 Rapport sauvegardé : {Path(rapport_fichier).name}")
    print()


if __name__ == "__main__":
    main()
