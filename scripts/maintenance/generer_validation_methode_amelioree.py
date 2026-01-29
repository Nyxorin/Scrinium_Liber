#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les fichiers de validation pour les inversions de la MÉTHODE AMÉLIORÉE
Fichiers avec colonne ACTION pour validation manuelle
"""

import csv
from pathlib import Path


def generer_csv_validation_amelioree():
    """Génère des CSV de validation par tranche de score"""

    fichier_certaines = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/inversions_certaines_methode_amelioree.csv"
    fichier_probables = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/inversions_probables_methode_amelioree.csv"
    dossier_sortie = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_amelioree"

    # Créer le dossier de sortie
    Path(dossier_sortie).mkdir(exist_ok=True)

    print("=" * 80)
    print("GÉNÉRATION DES FICHIERS DE VALIDATION - MÉTHODE AMÉLIORÉE")
    print("=" * 80)
    print()

    # Lire les inversions probables
    inversions_probables = []
    with open(fichier_probables, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            inversions_probables.append(row)

    print(f"📊 Total inversions probables : {len(inversions_probables)}")
    print()

    # Définir les tranches pour les probables
    tranches_probables = {
        'tres_haute_95-99': (95, 99),
        'haute_90-94': (90, 94),
        'haute_85-89': (85, 89),
        'moyenne_haute_80-84': (80, 84),
        'moyenne_75-79': (75, 79),
        'moyenne_70-74': (70, 74),
        'basse_60-69': (60, 69)
    }

    # Répartir par tranche
    for nom_tranche, (score_min, score_max) in tranches_probables.items():
        inversions_tranche = [
            inv for inv in inversions_probables
            if score_min <= int(inv['Score']) <= score_max
        ]

        if inversions_tranche:
            fichier_sortie = f"{dossier_sortie}/validation_{nom_tranche}.csv"
            generer_fichier_validation(inversions_tranche, fichier_sortie, nom_tranche, score_min, score_max)

    # Lire les inversions certaines
    inversions_certaines = []
    with open(fichier_certaines, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            inversions_certaines.append(row)

    print(f"\n📊 Total inversions certaines : {len(inversions_certaines)}")
    print()

    # Générer fichier pour les certaines aussi (au cas où)
    fichier_certaines_validation = f"{dossier_sortie}/validation_certaines_100+.csv"
    generer_fichier_validation(inversions_certaines, fichier_certaines_validation,
                               "certaines_100+", 100, 999)

    print()
    print("=" * 80)
    print("✅ TOUS LES FICHIERS DE VALIDATION SONT CRÉÉS")
    print("=" * 80)
    print(f"\n📁 Emplacement : {dossier_sortie}/")
    print()
    print("💡 Conseil : Commencez par les tranches avec haute confiance :")
    print(f"   1. validation_certaines_100+.csv ({len(inversions_certaines)} cas - confiance ~99%)")

    for nom_tranche, (score_min, score_max) in tranches_probables.items():
        count = len([inv for inv in inversions_probables if score_min <= int(inv['Score']) <= score_max])
        if count > 0:
            if score_min >= 95:
                prob = "~98%"
            elif score_min >= 90:
                prob = "~95%"
            elif score_min >= 85:
                prob = "~92%"
            elif score_min >= 80:
                prob = "~88%"
            elif score_min >= 75:
                prob = "~85%"
            elif score_min >= 70:
                prob = "~80%"
            else:
                prob = "~75%"

            priorite = "🔴🔴🔴" if score_min >= 95 else "🔴🔴" if score_min >= 90 else "🔴" if score_min >= 85 else "🟠" if score_min >= 75 else "🟡"

            print(f"   {priorite} validation_{nom_tranche}.csv ({count} cas - confiance {prob})")

    print()
    print("⏭️  Étape suivante : Ouvrez les fichiers dans Excel et validez")


def generer_fichier_validation(inversions: list, fichier_sortie: str,
                                nom_tranche: str, score_min: int, score_max: int):
    """Génère un fichier de validation avec colonne ACTION"""

    # Probabilité estimée
    if score_min >= 100:
        prob = "~99%"
    elif score_min >= 95:
        prob = "~98%"
    elif score_min >= 90:
        prob = "~95%"
    elif score_min >= 85:
        prob = "~92%"
    elif score_min >= 80:
        prob = "~88%"
    elif score_min >= 75:
        prob = "~85%"
    elif score_min >= 70:
        prob = "~80%"
    else:
        prob = "~75%"

    with open(fichier_sortie, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'ID',
            'Fichier',
            'Titre_actuel',
            'Auteur_actuel',
            'ACTION',  # Colonne pour l'utilisateur
            'Score',
            'Confiance',
            'Règles',
            'Titre_corrigé',
            'Auteur_corrigé'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        # Ligne d'instructions
        writer.writerow({
            'ID': '→',
            'Fichier': 'INSTRUCTIONS: Remplissez la colonne ACTION',
            'Titre_actuel': 'Laissez VIDE ou "OK" pour INVERSER',
            'Auteur_actuel': 'Mettez "X" ou "NON" pour NE PAS inverser',
            'ACTION': '← ICI',
            'Score': '→',
            'Confiance': f'Prob {prob}',
            'Règles': '→',
            'Titre_corrigé': '→',
            'Auteur_corrigé': '→'
        })

        # Écrire les inversions
        for idx, inv in enumerate(inversions, start=1):
            writer.writerow({
                'ID': idx,
                'Fichier': inv['Fichier'],
                'Titre_actuel': inv['Titre_actuel'],
                'Auteur_actuel': inv['Auteur_actuel'],
                'ACTION': '',  # Vide par défaut
                'Score': inv['Score'],
                'Confiance': inv['Confiance'],
                'Règles': inv['Règles'],
                'Titre_corrigé': inv['Titre_corrigé'],
                'Auteur_corrigé': inv['Auteur_corrigé']
            })

    print(f"✅ Fichier créé : validation_{nom_tranche}.csv ({len(inversions)} inversions)")


if __name__ == "__main__":
    generer_csv_validation_amelioree()
