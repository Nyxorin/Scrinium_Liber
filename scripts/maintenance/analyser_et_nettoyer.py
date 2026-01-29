#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse tous les fichiers du projet et identifie ceux qui sont obsolètes
Crée une archive des fichiers à supprimer
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Répertoire du projet
PROJET_DIR = Path("/Users/parisis/kDrive/Python Projets/Scrinium_Liber")


def analyser_fichiers():
    """Analyse tous les fichiers et les catégorise"""

    fichiers = {
        'scripts_actuels': [],      # Scripts Python actifs et utilisés
        'scripts_obsoletes': [],    # Scripts Python obsolètes
        'docs_actuelles': [],       # Documentation à garder
        'docs_obsoletes': [],       # Documentation obsolète/redondante
        'rapports_temp': [],        # Rapports temporaires
        'backups': [],              # Fichiers backup
        'config': [],               # Fichiers de configuration
        'donnees_temp': []          # Données temporaires
    }

    # ============================================================================
    # SCRIPTS PYTHON ACTUELS (À GARDER)
    # ============================================================================
    scripts_actuels = [
        'appliquer_validations.py',              # ✅ Script principal d'application
        'appliquer_maintenant.py',               # ✅ Script d'application sans confirmation
        'test_validation.py',                    # ✅ Script de test
        'generer_validation_methode_amelioree.py',  # ✅ Génération fichiers validation
        'detecter_inversions_avec_base_locale.py',  # ✅ Méthode améliorée de détection
        'auto_cleaner.py',                       # ✅ Nettoyage automatique
        'convertir_numbers_vers_csv.py',         # ✅ Conversion Numbers
    ]

    # ============================================================================
    # SCRIPTS OBSOLÈTES (À ARCHIVER)
    # ============================================================================
    scripts_obsoletes = [
        'appliquer_inversions_validees.py',      # Remplacé par appliquer_validations.py
        'appliquer_inversions_validees_amelioree.py',  # Remplacé
        'detecter_inversions_sans_api.py',       # Ancienne méthode (remplacée)
        'generer_csv_validation.py',             # Remplacé par version améliorée
        'appliquer_phases_456.py',               # Ancien workflow
        'analyser_inversions_probables.py',      # Analyse déjà faite
        'analyser_avec_dict_enrichi.py',         # Analyse terminée
        'analyser_categories_erreurs.py',        # Analyse terminée
        'check_megalex.py',                      # Vérification terminée
        'corriger_mon_livre.py',                 # Script spécifique obsolète
        'detecteur_final.py',                    # Remplacé
        'enrichir_dictionnaire.py',              # Enrichissement terminé
        'extraire_mots_manquants.py',            # Extraction terminée
        'filtrer_avec_api.py',                   # Filtrage terminé
        'filtrer_vrais_mots_francais.py',        # Filtrage terminé
        'migrer_projet.py',                      # Migration terminée
        'nettoyer_dictionnaire.py',              # Nettoyage terminé
        'nettoyer_projet.py',                    # Nettoyage terminé
        'valider_mots_avec_web.py',              # Validation terminée
        'verifier_mots_manquants.py',            # Vérification terminée
    ]

    # ============================================================================
    # DOCUMENTATION ACTUELLE (À GARDER)
    # ============================================================================
    docs_actuelles = [
        'README.md',                             # ✅ README principal
        'DEMARRAGE_RAPIDE_NUMBERS.md',          # ✅ Guide pour Numbers (actuel)
        'GUIDE_VALIDATION_NUMBERS_SIMPLIFIE.md',  # ✅ Guide simplifié (actuel)
        'GUIDE_VALIDATION_AMELIOREE.md',         # ✅ Guide méthode améliorée
        'EXPLICATION_METHODE_AMELIOREE.md',     # ✅ Explications méthode améliorée
        'BILAN_INVERSIONS_INCERTAINES.md',      # ✅ Bilan important
        'requirements.txt',                      # ✅ Dépendances Python
        'install.sh',                            # ✅ Script d'installation
    ]

    # ============================================================================
    # DOCUMENTATION OBSOLÈTE (À ARCHIVER)
    # ============================================================================
    docs_obsoletes = [
        'DEMARRAGE_RAPIDE.md',                   # Remplacé par version Numbers
        'GUIDE_MIGRATION.md',                    # Migration terminée
        'GUIDE_UTILISATION.md',                  # Remplacé par guides plus récents
        'GUIDE_UTILISATION_SIMPLE.md',           # Remplacé
        'GUIDE_VALIDATION_INVERSIONS.md',        # Remplacé par version améliorée
        'GUIDE_VALIDATION_NUMBERS.md',           # Remplacé par version simplifiée
        'INDEX_COMPLET_INVERSIONS.md',           # Index ancien
        'INDEX_DETECTION_INVERSIONS.md',         # Index ancien
        'INDEX_PROJET.md',                       # Index ancien
        'LISEZ_MOI_EN_PREMIER.txt',              # Ancien guide
        'MODE_EMPLOI_SIMPLE.md',                 # Remplacé
        'QUICK_START_INVERSIONS.md',             # Remplacé
        'README_VALIDATION.md',                  # Remplacé
        'REPONSE_COLONNE_ACTION.md',             # Réponse ponctuelle archivée
        'REPONSE_QUESTIONS_UTILISATEUR.md',      # Réponses ponctuelles
        'RESUME_DETECTION_INVERSIONS.md',        # Résumé ancien
        'START_HERE.md',                         # Remplacé
        'REGLES_DETECTION_INVERSIONS.md',        # Anciennes règles
        'EXEMPLES_INVERSIONS_DETECTEES.md',      # Exemples ancienne méthode
        'PROBABILITES_INVERSIONS_PROBABLES.md',  # Stats ancienne méthode
        'DICTIONNAIRE_MEGALEX_INFO.md',          # Info Megalex (archivable)
        'ENRICHISSEMENT_DICTIONNAIRE.md',        # Enrichissement terminé
        'PLAN_ORGANISATION_EBOOKS.md',           # Plan ancien
        'NETTOYAGE_EFFECTUE.md',                 # Nettoyage ancien
        'CONCLUSION_FILTRAGE.md',                # Conclusion filtrage terminé
    ]

    # ============================================================================
    # RAPPORTS TEMPORAIRES (À ARCHIVER)
    # ============================================================================
    rapports_temp = [
        'ANALYSE_DETAILLEE_FINALE.txt',
        'ERREURS_REELLES_FINALES.txt',
        'MIGRATION_RAPPORT.txt',
        'RAPPORT_ANALYSE_DICT_ENRICHI.txt',
        'RAPPORT_FILTRAGE.txt',
        'RAPPORT_PHASE5_SEMI_AUTO.txt',
        'RAPPORT_PHASE6_ASSISTEE.txt',
        'SYNTHESE_ANALYSE_FINALE.md',
        'migration_info.txt',
    ]

    # ============================================================================
    # DONNÉES TEMPORAIRES (À ARCHIVER)
    # ============================================================================
    donnees_temp = [
        'learned_rules.txt',
        'smart_learned_rules.txt',
        'mots_a_ajouter_top_1000.txt',
        'mots_douteux_a_verifier.txt',
        'mots_grammaticaux_manquants.txt',
        'mots_grammaticaux_supplementaires.txt',
        'mots_grammaticaux_supplementaires_backup_20251029_143202.txt',
        'mots_manquants_avec_frequences.txt',
        'mots_rejetes_ameliores.txt',
        'mots_rejetes_erreurs_ocr.txt',
        'mots_valides_ameliores.txt',
        'mots_valides_filtres.txt',
    ]

    # Remplir les catégories
    for script in scripts_actuels:
        if (PROJET_DIR / script).exists():
            fichiers['scripts_actuels'].append(script)

    for script in scripts_obsoletes:
        if (PROJET_DIR / script).exists():
            fichiers['scripts_obsoletes'].append(script)

    for doc in docs_actuelles:
        if (PROJET_DIR / doc).exists():
            fichiers['docs_actuelles'].append(doc)

    for doc in docs_obsoletes:
        if (PROJET_DIR / doc).exists():
            fichiers['docs_obsoletes'].append(doc)

    for rapport in rapports_temp:
        if (PROJET_DIR / rapport).exists():
            fichiers['rapports_temp'].append(rapport)

    for donnee in donnees_temp:
        if (PROJET_DIR / donnee).exists():
            fichiers['donnees_temp'].append(donnee)

    return fichiers


def creer_rapport(fichiers):
    """Crée un rapport d'analyse"""

    print("=" * 80)
    print("ANALYSE DES FICHIERS DU PROJET SCRINIUM_LIBER")
    print("=" * 80)
    print()

    # Fichiers à conserver
    total_garder = len(fichiers['scripts_actuels']) + len(fichiers['docs_actuelles'])
    print(f"📁 FICHIERS À CONSERVER : {total_garder}")
    print("-" * 80)
    print()

    print("✅ Scripts Python actifs :")
    for f in sorted(fichiers['scripts_actuels']):
        print(f"   • {f}")
    print()

    print("✅ Documentation actuelle :")
    for f in sorted(fichiers['docs_actuelles']):
        print(f"   • {f}")
    print()

    # Fichiers à archiver
    total_archiver = (len(fichiers['scripts_obsoletes']) +
                     len(fichiers['docs_obsoletes']) +
                     len(fichiers['rapports_temp']) +
                     len(fichiers['donnees_temp']))

    print("=" * 80)
    print(f"📦 FICHIERS À ARCHIVER : {total_archiver}")
    print("-" * 80)
    print()

    print(f"🗑️  Scripts obsolètes ({len(fichiers['scripts_obsoletes'])}) :")
    for f in sorted(fichiers['scripts_obsoletes']):
        print(f"   • {f}")
    print()

    print(f"🗑️  Documentation obsolète ({len(fichiers['docs_obsoletes'])}) :")
    for f in sorted(fichiers['docs_obsoletes']):
        print(f"   • {f}")
    print()

    print(f"🗑️  Rapports temporaires ({len(fichiers['rapports_temp'])}) :")
    for f in sorted(fichiers['rapports_temp']):
        print(f"   • {f}")
    print()

    print(f"🗑️  Données temporaires ({len(fichiers['donnees_temp'])}) :")
    for f in sorted(fichiers['donnees_temp']):
        print(f"   • {f}")
    print()

    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Fichiers à conserver  : {total_garder}")
    print(f"Fichiers à archiver   : {total_archiver}")
    print()

    return total_archiver


def creer_archive(fichiers):
    """Crée une archive des fichiers obsolètes"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = PROJET_DIR / f"archive_nettoyage_{timestamp}"
    archive_dir.mkdir(exist_ok=True)

    print(f"📦 Création de l'archive : {archive_dir.name}")
    print()

    # Créer les sous-dossiers
    (archive_dir / "scripts_obsoletes").mkdir(exist_ok=True)
    (archive_dir / "docs_obsoletes").mkdir(exist_ok=True)
    (archive_dir / "rapports_temp").mkdir(exist_ok=True)
    (archive_dir / "donnees_temp").mkdir(exist_ok=True)

    compteur = 0

    # Déplacer les fichiers
    for script in fichiers['scripts_obsoletes']:
        src = PROJET_DIR / script
        dst = archive_dir / "scripts_obsoletes" / script
        shutil.move(str(src), str(dst))
        print(f"   ✅ {script}")
        compteur += 1

    for doc in fichiers['docs_obsoletes']:
        src = PROJET_DIR / doc
        dst = archive_dir / "docs_obsoletes" / doc
        shutil.move(str(src), str(dst))
        print(f"   ✅ {doc}")
        compteur += 1

    for rapport in fichiers['rapports_temp']:
        src = PROJET_DIR / rapport
        dst = archive_dir / "rapports_temp" / rapport
        shutil.move(str(src), str(dst))
        print(f"   ✅ {rapport}")
        compteur += 1

    for donnee in fichiers['donnees_temp']:
        src = PROJET_DIR / donnee
        dst = archive_dir / "donnees_temp" / donnee
        shutil.move(str(src), str(dst))
        print(f"   ✅ {donnee}")
        compteur += 1

    # Créer un fichier README dans l'archive
    readme_content = f"""# Archive de Nettoyage Scrinium_Liber

Date de création : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Contenu

Cette archive contient {compteur} fichiers obsolètes ou temporaires qui ont été retirés du projet principal.

### Scripts obsolètes ({len(fichiers['scripts_obsoletes'])})
Anciens scripts Python remplacés par de nouvelles versions.

### Documentation obsolète ({len(fichiers['docs_obsoletes'])})
Anciens guides et documentations remplacés par des versions plus récentes.

### Rapports temporaires ({len(fichiers['rapports_temp'])})
Rapports d'analyse et de migration qui ont servi pendant le développement.

### Données temporaires ({len(fichiers['donnees_temp'])})
Fichiers de données intermédiaires générés pendant les phases de développement.

## Restauration

Pour restaurer un fichier :
```bash
cp archive_nettoyage_{timestamp}/[categorie]/[fichier] ./
```

## Conservation

Cette archive peut être supprimée après quelques semaines si aucun problème n'est détecté.
"""

    with open(archive_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print()
    print(f"✅ {compteur} fichiers archivés dans : {archive_dir.name}/")

    return archive_dir


def main():
    """Fonction principale"""

    print()

    # Analyser les fichiers
    fichiers = analyser_fichiers()

    # Créer le rapport
    total_archiver = creer_rapport(fichiers)

    if total_archiver == 0:
        print("✅ Aucun fichier à archiver.")
        return

    # Créer l'archive
    print("=" * 80)
    print("CRÉATION DE L'ARCHIVE")
    print("=" * 80)
    print()

    archive_dir = creer_archive(fichiers)

    print()
    print("=" * 80)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 80)
    print()
    print(f"📦 Archive créée : {archive_dir.name}/")
    print(f"📁 Fichiers conservés dans le projet : {len(fichiers['scripts_actuels']) + len(fichiers['docs_actuelles'])}")
    print()
    print("💡 L'archive peut être supprimée après quelques semaines si tout fonctionne bien.")
    print()


if __name__ == "__main__":
    main()
