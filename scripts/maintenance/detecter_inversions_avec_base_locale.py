#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Détection d'inversions AMÉLIORÉE utilisant la base d'auteurs existante
Principe : Si TOUS les auteurs sont au format "Nom, Prénom",
alors un titre au format "Nom, Prénom" est forcément une inversion !
"""

import csv
import re
from collections import defaultdict, Counter
from typing import Set, Dict, Tuple


class DetecteurInversionsAmeliore:
    """Détection basée sur l'analyse de la base existante"""

    def __init__(self):
        self.auteurs_connus = set()  # Format "Nom, Prénom" extraits de la base
        self.noms_auteurs = set()    # Juste les noms de famille
        self.prenoms_auteurs = set() # Juste les prénoms
        self.stats = defaultdict(int)

    def analyser_base_existante(self, fichier_csv: str):
        """
        Analyse validation_humaine.csv pour extraire tous les auteurs connus
        """
        print("🔍 Analyse de la base d'auteurs existante...")
        print("=" * 80)

        with open(fichier_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                auteur = row.get('Auteur(s)', '').strip()

                if not auteur:
                    continue

                # Détecter le format "Nom, Prénom"
                if ',' in auteur and not auteur.startswith(('Le ', 'La ', 'Les ', 'L\'')):
                    # Pattern : "Nom, Prénom" ou "Nom1 & Nom2, Prénom1 & Prénom2"
                    parties = auteur.split(';')  # Gérer multi-auteurs séparés par ;

                    for partie in parties:
                        partie = partie.strip()

                        # Format simple "Nom, Prénom"
                        if re.match(r'^[A-ZÀ-Ö][a-zà-ö\'-]+,\s+[A-ZÀ-Ö]', partie):
                            self.auteurs_connus.add(partie)

                            # Extraire nom et prénom
                            if ',' in partie:
                                nom, prenom = partie.split(',', 1)
                                self.noms_auteurs.add(nom.strip())
                                self.prenoms_auteurs.add(prenom.strip())

        print(f"✅ {len(self.auteurs_connus)} auteurs au format 'Nom, Prénom' trouvés")
        print(f"✅ {len(self.noms_auteurs)} noms de famille distincts")
        print(f"✅ {len(self.prenoms_auteurs)} prénoms distincts")
        print()

        # Afficher quelques exemples
        print("📝 Exemples d'auteurs détectés :")
        for auteur in list(self.auteurs_connus)[:10]:
            print(f"   • {auteur}")
        print()

    def detecter_inversion(self, titre: str, auteur: str, fichier: str = "") -> Dict:
        """
        Détection basée sur la base d'auteurs connus

        Logique simple et puissante :
        1. Si le TITRE est au format "Nom, Prénom" → INVERSION (auteur dans mauvais champ)
        2. Si l'AUTEUR n'est PAS au format "Nom, Prénom" → INVERSION POSSIBLE
        3. Si le TITRE correspond à un auteur connu → INVERSION CERTAINE
        """

        score = 0
        regles = []
        confiance = "DOUTEUX"

        # RÈGLE 1 : Le titre est-il au format "Nom, Prénom" ?
        if re.match(r'^[A-ZÀ-Ö][a-zà-ö\'-]+,\s+[A-ZÀ-Ö]', titre):
            score += 80  # Très fort
            regles.append("Format 'Nom, Prénom' dans le TITRE")

        # RÈGLE 2 : Le titre correspond-il exactement à un auteur connu ?
        if titre in self.auteurs_connus:
            score += 100  # Quasi certain !
            regles.append("Auteur connu trouvé dans le TITRE")

        # RÈGLE 3 : L'auteur n'est-il PAS au format standard ?
        if ',' not in auteur or auteur.startswith(('Le ', 'La ', 'Les ', 'L\'')):
            score += 30
            regles.append("Auteur n'est pas au format standard")

        # RÈGLE 4 : L'auteur se termine par un article (titre typique)
        if re.search(r',\s+(Le|La|Les|L\')$', auteur):
            score += 50
            regles.append("Article défini en fin d'AUTEUR")

        # RÈGLE 5 : L'auteur contient des chiffres (tome, etc.)
        if re.search(r'\d', auteur):
            score += 40
            regles.append("Chiffres dans AUTEUR")

        # RÈGLE 6 : L'auteur contient des mots-clés de titres
        mots_cles_titres = ['Tome', 'Volume', 'Partie', 'Roman', 'Nouvelles', 'Oeuvres']
        if any(mot in auteur for mot in mots_cles_titres):
            score += 40
            regles.append("Mots-clés de titre dans AUTEUR")

        # RÈGLE 7 : Le nom dans le titre correspond à un nom d'auteur connu
        if ',' in titre:
            nom_dans_titre = titre.split(',')[0].strip()
            if nom_dans_titre in self.noms_auteurs:
                score += 60
                regles.append(f"Nom d'auteur connu '{nom_dans_titre}' dans TITRE")

        # Déterminer la confiance
        if score >= 100:
            confiance = "CERTAIN"
            inversion = True
        elif score >= 60:
            confiance = "PROBABLE"
            inversion = True
        else:
            confiance = "DOUTEUX"
            inversion = False

        return {
            'fichier': fichier,
            'titre_actuel': titre,
            'auteur_actuel': auteur,
            'score': score,
            'confiance': confiance,
            'regles': regles,
            'inversion': inversion,
            'titre_corrige': auteur,
            'auteur_corrige': titre
        }

    def analyser_fichier_complet(self, fichier_csv: str):
        """Analyse complète du fichier"""

        inversions_certaines = []
        inversions_probables = []
        inversions_douteuses = []

        print("🔍 Analyse des inversions potentielles...")
        print("=" * 80)
        print()

        with open(fichier_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                fichier = row.get('Fichier', '')
                titre = row.get('Titre', '').strip()
                auteur = row.get('Auteur(s)', '').strip()

                if not titre or not auteur:
                    continue

                resultat = self.detecter_inversion(titre, auteur, fichier)

                if resultat['confiance'] == 'CERTAIN':
                    inversions_certaines.append(resultat)
                    self.stats['certaines'] += 1
                elif resultat['confiance'] == 'PROBABLE':
                    inversions_probables.append(resultat)
                    self.stats['probables'] += 1
                else:
                    inversions_douteuses.append(resultat)
                    self.stats['douteuses'] += 1

                self.stats['total'] += 1

        print("✅ Analyse terminée")
        print()
        print("📊 RÉSULTATS")
        print("=" * 80)
        print(f"Total d'entrées analysées : {self.stats['total']}")
        print(f"Inversions CERTAINES (≥100) : {self.stats['certaines']}")
        print(f"Inversions PROBABLES (60-99): {self.stats['probables']}")
        print(f"Inversions DOUTEUSES (<60)  : {self.stats['douteuses']}")
        print()

        return inversions_certaines, inversions_probables, inversions_douteuses

    def comparer_avec_ancienne_methode(self, fichier_anciennes_inversions: str,
                                       nouvelles_certaines: list,
                                       nouvelles_probables: list):
        """
        Compare avec les résultats de l'ancienne méthode
        """
        print("🔄 Comparaison avec l'ancienne méthode...")
        print("=" * 80)
        print()

        # Lire anciennes inversions
        anciennes_certaines = []
        anciennes_probables = []

        with open(fichier_anciennes_inversions, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                score = int(row['Score'])
                if score >= 90:
                    anciennes_certaines.append(row['Fichier'])
                elif score >= 50:
                    anciennes_probables.append(row['Fichier'])

        # Nouvelles inversions
        nouvelles_certaines_fichiers = set(inv['fichier'] for inv in nouvelles_certaines)
        nouvelles_probables_fichiers = set(inv['fichier'] for inv in nouvelles_probables)

        # Analyse
        print("📊 COMPARAISON")
        print("-" * 80)
        print(f"\nANCIENNE MÉTHODE :")
        print(f"  • Certaines : {len(anciennes_certaines)}")
        print(f"  • Probables : {len(anciennes_probables)}")
        print(f"  • TOTAL     : {len(anciennes_certaines) + len(anciennes_probables)}")

        print(f"\nNOUVELLE MÉTHODE (avec base locale) :")
        print(f"  • Certaines : {len(nouvelles_certaines_fichiers)}")
        print(f"  • Probables : {len(nouvelles_probables_fichiers)}")
        print(f"  • TOTAL     : {len(nouvelles_certaines_fichiers) + len(nouvelles_probables_fichiers)}")

        # Différences
        nouvelles_en_plus = nouvelles_certaines_fichiers - set(anciennes_certaines)
        anciennes_en_plus = set(anciennes_certaines) - nouvelles_certaines_fichiers

        print(f"\nDIFFÉRENCES :")
        print(f"  • Nouvelles certaines détectées : {len(nouvelles_en_plus)}")
        print(f"  • Anciennes certaines non détectées : {len(anciennes_en_plus)}")
        print()

        if nouvelles_en_plus:
            print("📝 Exemples de nouvelles inversions certaines détectées :")
            for fichier in list(nouvelles_en_plus)[:5]:
                # Trouver l'inversion
                inv = next((i for i in nouvelles_certaines if i['fichier'] == fichier), None)
                if inv:
                    print(f"\n   📁 {fichier}")
                    print(f"      Titre : {inv['titre_actuel']}")
                    print(f"      Auteur: {inv['auteur_actuel']}")
                    print(f"      Score : {inv['score']}")
                    print(f"      Règles: {', '.join(inv['regles'])}")

    def exporter_resultats(self, certaines: list, probables: list,
                          dossier_sortie: str):
        """Exporte les résultats"""

        import os
        os.makedirs(dossier_sortie, exist_ok=True)

        # Export certaines
        fichier_certaines = f"{dossier_sortie}/inversions_certaines_methode_amelioree.csv"
        with open(fichier_certaines, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['Fichier', 'Titre_actuel', 'Auteur_actuel', 'Score',
                         'Confiance', 'Règles', 'Titre_corrigé', 'Auteur_corrigé']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for inv in certaines:
                writer.writerow({
                    'Fichier': inv['fichier'],
                    'Titre_actuel': inv['titre_actuel'],
                    'Auteur_actuel': inv['auteur_actuel'],
                    'Score': inv['score'],
                    'Confiance': inv['confiance'],
                    'Règles': ' | '.join(inv['regles']),
                    'Titre_corrigé': inv['titre_corrige'],
                    'Auteur_corrigé': inv['auteur_corrige']
                })

        print(f"✅ Inversions certaines exportées : {fichier_certaines}")

        # Export probables
        fichier_probables = f"{dossier_sortie}/inversions_probables_methode_amelioree.csv"
        with open(fichier_probables, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['Fichier', 'Titre_actuel', 'Auteur_actuel', 'Score',
                         'Confiance', 'Règles', 'Titre_corrigé', 'Auteur_corrigé']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for inv in probables:
                writer.writerow({
                    'Fichier': inv['fichier'],
                    'Titre_actuel': inv['titre_actuel'],
                    'Auteur_actuel': inv['auteur_actuel'],
                    'Score': inv['score'],
                    'Confiance': inv['confiance'],
                    'Règles': ' | '.join(inv['regles']),
                    'Titre_corrigé': inv['titre_corrige'],
                    'Auteur_corrigé': inv['auteur_corrige']
                })

        print(f"✅ Inversions probables exportées : {fichier_probables}")


def main():
    """Fonction principale"""

    fichier_base = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_humaine.csv"
    fichier_anciennes = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/inversions_detectees.csv"
    dossier_sortie = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer"

    print("=" * 80)
    print("DÉTECTION D'INVERSIONS - MÉTHODE AMÉLIORÉE")
    print("Utilise la base d'auteurs existante pour améliorer la détection")
    print("=" * 80)
    print()

    # Créer le détecteur
    detecteur = DetecteurInversionsAmeliore()

    # 1. Analyser la base existante pour extraire les auteurs
    detecteur.analyser_base_existante(fichier_base)

    # 2. Analyser le fichier complet
    certaines, probables, douteuses = detecteur.analyser_fichier_complet(fichier_base)

    # 3. Comparer avec ancienne méthode
    if os.path.exists(fichier_anciennes):
        detecteur.comparer_avec_ancienne_methode(fichier_anciennes, certaines, probables)

    # 4. Exporter
    detecteur.exporter_resultats(certaines, probables, dossier_sortie)

    # 5. Afficher des exemples
    print()
    print("=" * 80)
    print("EXEMPLES D'INVERSIONS CERTAINES DÉTECTÉES")
    print("=" * 80)
    print()

    for inv in certaines[:10]:
        print(f"📁 {inv['fichier']}")
        print(f"   ❌ AVANT : Titre='{inv['titre_actuel']}' | Auteur='{inv['auteur_actuel']}'")
        print(f"   ✅ APRÈS : Titre='{inv['titre_corrige']}' | Auteur='{inv['auteur_corrige']}'")
        print(f"   📊 Score={inv['score']} | Règles: {', '.join(inv['regles'])}")
        print()


if __name__ == "__main__":
    import os
    main()
