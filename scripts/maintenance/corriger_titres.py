#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction automatique des titres de livres
Corrige tous les problèmes détectés dans l'analyse
"""

import csv
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class CorrecteurTitres:
    """Corrige les anomalies dans les titres"""

    def __init__(self):
        self.corrections = defaultdict(list)
        self.stats = defaultdict(int)

    def corriger_article_inverse(self, titre):
        """
        Corrige les articles inversés
        Ex: "Ile Atlantique, L'" -> "L'Ile Atlantique"
        """

        # Pattern : titre, Le/La/Les/L'
        patterns = [
            (r'^(.+),\s+(Le)$', lambda m: f"{m.group(2)} {m.group(1)}"),
            (r'^(.+),\s+(La)$', lambda m: f"{m.group(2)} {m.group(1)}"),
            (r'^(.+),\s+(Les)$', lambda m: f"{m.group(2)} {m.group(1)}"),
            (r"^(.+),\s+(L')$", lambda m: f"{m.group(2)}{m.group(1)}"),
            (r'^(.+),\s+(Un)$', lambda m: f"{m.group(2)} {m.group(1)}"),
            (r'^(.+),\s+(Une)$', lambda m: f"{m.group(2)} {m.group(1)}"),
            (r'^(.+),\s+(Des)$', lambda m: f"{m.group(2)} {m.group(1)}"),
        ]

        for pattern, replacer in patterns:
            match = re.match(pattern, titre)
            if match:
                nouveau_titre = replacer(match)
                # Mettre la première lettre en majuscule
                if nouveau_titre and nouveau_titre[0].islower():
                    nouveau_titre = nouveau_titre[0].upper() + nouveau_titre[1:]
                return nouveau_titre, "Article inversé corrigé"

        return titre, None

    def nettoyer_underscores(self, titre):
        """
        Remplace les underscores par des espaces
        Sauf ceux qui entourent du texte (italique)
        """

        # Cas 1 : underscores pour italique _texte_ -> conserver
        # Cas 2 : underscores comme séparateurs -> remplacer par espaces

        modifie = False

        # Remplacer les underscores isolés ou multiples par espaces
        nouveau_titre = re.sub(r'_+', ' ', titre)

        if nouveau_titre != titre:
            modifie = True

        # Nettoyer les espaces multiples résultants
        nouveau_titre = re.sub(r'\s+', ' ', nouveau_titre).strip()

        if modifie:
            return nouveau_titre, "Underscores remplacés"
        return titre, None

    def normaliser_espaces(self, titre):
        """Normalise les espaces multiples"""

        nouveau_titre = re.sub(r'\s+', ' ', titre).strip()

        if nouveau_titre != titre:
            return nouveau_titre, "Espaces normalisés"
        return titre, None

    def normaliser_casse(self, titre):
        """
        Normalise la casse des titres tout en MAJUSCULES
        Ex: "HERBE ROUGE, L'" -> "Herbe rouge, L'"
        """

        if titre.isupper() and len(titre) > 10:
            # Convertir en casse normale (première lettre de chaque mot en majuscule)
            nouveau_titre = titre.title()
            return nouveau_titre, "Casse normalisée"

        return titre, None

    def supprimer_metadonnees(self, titre):
        """
        Supprime les métadonnées parasites
        Ex: "Mon livre french.zzz" -> "Mon livre"
        """

        modifie = False

        # Liste des métadonnées à supprimer
        patterns_a_supprimer = [
            r'\s+french\b',
            r'\s+\.zzz\b',
            r'\s+\.Z\b',
            r'\s+\(French Edition\)',
            r'\s+french\.zzz',
            r'\s+french\.Z',
        ]

        nouveau_titre = titre

        for pattern in patterns_a_supprimer:
            nouveau_nouveau = re.sub(pattern, '', nouveau_titre, flags=re.IGNORECASE)
            if nouveau_nouveau != nouveau_titre:
                modifie = True
                nouveau_titre = nouveau_nouveau

        # Nettoyer les espaces résultants
        nouveau_titre = re.sub(r'\s+', ' ', nouveau_titre).strip()

        if modifie:
            return nouveau_titre, "Métadonnées supprimées"
        return titre, None

    def corriger_titre(self, titre):
        """
        Applique toutes les corrections sur un titre
        Retourne (nouveau_titre, liste_corrections)
        """

        corrections = []
        titre_courant = titre

        # 1. Corriger article inversé (priorité haute)
        titre_courant, correction = self.corriger_article_inverse(titre_courant)
        if correction:
            corrections.append(correction)

        # 2. Nettoyer underscores
        titre_courant, correction = self.nettoyer_underscores(titre_courant)
        if correction:
            corrections.append(correction)

        # 3. Normaliser espaces
        titre_courant, correction = self.normaliser_espaces(titre_courant)
        if correction:
            corrections.append(correction)

        # 4. Normaliser casse
        titre_courant, correction = self.normaliser_casse(titre_courant)
        if correction:
            corrections.append(correction)

        # 5. Supprimer métadonnées
        titre_courant, correction = self.supprimer_metadonnees(titre_courant)
        if correction:
            corrections.append(correction)

        return titre_courant, corrections

    def analyser_corrections(self, fichier_csv):
        """Analyse les corrections à appliquer sans les appliquer"""

        print("=" * 80)
        print("ANALYSE DES CORRECTIONS À APPLIQUER")
        print("=" * 80)
        print()

        corrections_a_appliquer = []

        with open(fichier_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                titre_original = row.get('Titre', '').strip()
                auteur = row.get('Auteur(s)', '').strip()
                fichier = row.get('Fichier', '').strip()

                if not titre_original:
                    continue

                # Tenter la correction
                titre_corrige, liste_corrections = self.corriger_titre(titre_original)

                if liste_corrections:
                    corrections_a_appliquer.append({
                        'fichier': fichier,
                        'auteur': auteur,
                        'titre_original': titre_original,
                        'titre_corrige': titre_corrige,
                        'corrections': liste_corrections,
                        'row_complete': row
                    })

                    # Stats
                    for correction in liste_corrections:
                        self.stats[correction] += 1

        print(f"📊 Corrections à appliquer : {len(corrections_a_appliquer)}")
        print()

        # Afficher stats par type
        print("Par type de correction :")
        for type_correction, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {type_correction:<30} : {count:4d} titres")
        print()

        return corrections_a_appliquer

    def afficher_exemples(self, corrections_a_appliquer, n=10):
        """Affiche des exemples de corrections"""

        print("=" * 80)
        print(f"EXEMPLES DE CORRECTIONS (affichage de {n} premiers)")
        print("=" * 80)
        print()

        for i, correction in enumerate(corrections_a_appliquer[:n], 1):
            print(f"{i}. {correction['fichier'][:60]}")
            print(f"   ❌ AVANT : {correction['titre_original']}")
            print(f"   ✅ APRÈS : {correction['titre_corrige']}")
            print(f"   📝 Corrections : {', '.join(correction['corrections'])}")
            print()

    def appliquer_corrections(self, fichier_csv, corrections_a_appliquer, backup=True):
        """Applique réellement les corrections"""

        # Backup
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fichier_backup = fichier_csv.replace('.csv', f'_backup_corrections_{timestamp}.csv')
            shutil.copy2(fichier_csv, fichier_backup)
            print(f"📦 Backup créé : {Path(fichier_backup).name}")
            print()

        # Créer un index des corrections par fichier
        corrections_index = {c['fichier']: c for c in corrections_a_appliquer}

        # Lire et modifier
        lignes_modifiees = []
        compteur = 0

        with open(fichier_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            fieldnames = reader.fieldnames

            for row in reader:
                fichier = row.get('Fichier', '')

                # Si correction à appliquer
                if fichier in corrections_index:
                    correction = corrections_index[fichier]
                    row['Titre'] = correction['titre_corrige']
                    compteur += 1

                lignes_modifiees.append(row)

        # Écrire le fichier modifié
        with open(fichier_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(lignes_modifiees)

        return compteur

    def generer_rapport(self, corrections_a_appliquer, fichier_rapport):
        """Génère un rapport détaillé des corrections"""

        with open(fichier_rapport, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RAPPORT DE CORRECTIONS DES TITRES\n")
            f.write("=" * 80 + "\n")
            f.write(f"\nDate : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nTotal de corrections appliquées : {len(corrections_a_appliquer)}\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("STATISTIQUES PAR TYPE DE CORRECTION\n")
            f.write("=" * 80 + "\n\n")

            for type_correction, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{type_correction:<35} : {count:4d} titres\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("DÉTAIL DES CORRECTIONS\n")
            f.write("=" * 80 + "\n\n")

            for correction in corrections_a_appliquer:
                f.write(f"📁 {correction['fichier']}\n")
                f.write(f"   Auteur : {correction['auteur']}\n")
                f.write(f"   AVANT  : {correction['titre_original']}\n")
                f.write(f"   APRÈS  : {correction['titre_corrige']}\n")
                f.write(f"   Types  : {', '.join(correction['corrections'])}\n")
                f.write("\n")


def main():
    """Fonction principale"""

    fichier_csv = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_humaine.csv"
    fichier_rapport = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/rapport_corrections_titres.txt"

    print("=" * 80)
    print("CORRECTEUR AUTOMATIQUE DE TITRES")
    print("=" * 80)
    print()

    # Créer le correcteur
    correcteur = CorrecteurTitres()

    # Phase 1 : Analyser
    print("Phase 1 : Analyse des corrections nécessaires...")
    print()
    corrections_a_appliquer = correcteur.analyser_corrections(fichier_csv)

    if not corrections_a_appliquer:
        print("✅ Aucune correction nécessaire !")
        return

    # Phase 2 : Afficher exemples
    correcteur.afficher_exemples(corrections_a_appliquer, n=15)

    # Phase 3 : Appliquer
    print("=" * 80)
    print("APPLICATION DES CORRECTIONS")
    print("=" * 80)
    print()

    nb_corrections = correcteur.appliquer_corrections(fichier_csv, corrections_a_appliquer)

    print("=" * 80)
    print("✅ CORRECTIONS APPLIQUÉES AVEC SUCCÈS")
    print("=" * 80)
    print(f"Nombre de titres corrigés : {nb_corrections}")
    print(f"Fichier mis à jour : validation_humaine.csv")
    print()

    # Générer rapport
    correcteur.generer_rapport(corrections_a_appliquer, fichier_rapport)
    print(f"📄 Rapport détaillé : {Path(fichier_rapport).name}")
    print()


if __name__ == "__main__":
    main()
