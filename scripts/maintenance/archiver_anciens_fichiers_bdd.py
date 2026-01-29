#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archive tous les anciens fichiers de la base de données
Conserve uniquement validation_humaine.csv (version actuelle)
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def archiver_anciens_fichiers():
    """Archive tous les anciens fichiers validation_humaine sauf le principal"""

    ebook_dir = Path("/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer")

    # Créer le dossier d'archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = ebook_dir / f"archive_bdd_{timestamp}"
    archive_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("ARCHIVAGE DES ANCIENS FICHIERS DE BASE DE DONNÉES")
    print("=" * 80)
    print()

    # Fichier principal à conserver
    fichier_principal = "validation_humaine.csv"

    # Lister tous les fichiers validation_humaine*
    tous_fichiers = list(ebook_dir.glob("validation_humaine*"))

    fichiers_a_archiver = []

    for fichier in tous_fichiers:
        # Garder seulement le fichier principal
        if fichier.name == fichier_principal:
            continue
        fichiers_a_archiver.append(fichier)

    print(f"📁 Fichier principal conservé :")
    print(f"   ✅ {fichier_principal}")
    print()

    if not fichiers_a_archiver:
        print("✅ Aucun ancien fichier à archiver.")
        return

    print(f"📦 Fichiers à archiver : {len(fichiers_a_archiver)}")
    print("-" * 80)
    print()

    # Créer des sous-dossiers par type
    (archive_dir / "backups").mkdir(exist_ok=True)
    (archive_dir / "versions_anciennes").mkdir(exist_ok=True)
    (archive_dir / "autres").mkdir(exist_ok=True)

    compteur = 0
    total_size = 0

    for fichier in sorted(fichiers_a_archiver):
        taille = fichier.stat().st_size
        total_size += taille
        taille_mb = taille / (1024 * 1024)

        # Déterminer le sous-dossier de destination
        if "backup" in fichier.name:
            destination = archive_dir / "backups" / fichier.name
        elif "corrige" in fichier.name:
            destination = archive_dir / "versions_anciennes" / fichier.name
        elif fichier.suffix == ".numbers":
            destination = archive_dir / "autres" / fichier.name
        else:
            destination = archive_dir / "autres" / fichier.name

        # Déplacer le fichier
        shutil.move(str(fichier), str(destination))
        print(f"   ✅ {fichier.name} ({taille_mb:.1f} MB)")
        compteur += 1

    print()
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Fichiers archivés : {compteur}")
    print(f"Taille totale     : {total_size / (1024 * 1024):.1f} MB")
    print(f"Archive créée     : {archive_dir.name}/")
    print()

    # Créer un README dans l'archive
    readme_content = f"""# Archive Base de Données - {timestamp}

Date de création : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Contenu

Cette archive contient {compteur} anciens fichiers de la base de données validation_humaine.

### Structure

```
archive_bdd_{timestamp}/
├── backups/                   Fichiers de backup
├── versions_anciennes/        Anciennes versions corrigées
└── autres/                    Autres fichiers (.numbers, etc.)
```

### Fichier Principal Conservé

Le fichier principal actif reste dans le dossier parent :
```
ebook_organizer/validation_humaine.csv
```

**Date de dernière modification :** 2025-11-12 08:35:53
**Contenu :** 17 114 ebooks avec 4 111 inversions corrigées

## Restauration

Pour restaurer un fichier :
```bash
cp archive_bdd_{timestamp}/backups/nom_fichier.csv ../
```

## Conservation

Cette archive peut être supprimée après quelques mois si aucun problème n'est détecté.

**Recommandation :** Conserver au moins 1 mois pour sécurité.
"""

    with open(archive_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

    # Créer un fichier d'inventaire détaillé
    inventaire_content = f"""# Inventaire des Fichiers Archivés

Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Fichiers Archivés ({compteur})

"""

    for fichier in sorted(fichiers_a_archiver):
        if fichier.exists():
            continue  # Déjà déplacé

        # Trouver le fichier dans l'archive
        nom = fichier.name
        if "backup" in nom:
            chemin = f"backups/{nom}"
        elif "corrige" in nom:
            chemin = f"versions_anciennes/{nom}"
        else:
            chemin = f"autres/{nom}"

        inventaire_content += f"- {chemin}\n"

    with open(archive_dir / "INVENTAIRE.txt", 'w', encoding='utf-8') as f:
        f.write(inventaire_content)

    print("📄 README.md créé dans l'archive")
    print("📄 INVENTAIRE.txt créé dans l'archive")
    print()

    print("=" * 80)
    print("✅ ARCHIVAGE TERMINÉ")
    print("=" * 80)
    print()
    print(f"📦 Archive : ebook_organizer/{archive_dir.name}/")
    print(f"✅ Fichier actif : ebook_organizer/validation_humaine.csv")
    print()

    return archive_dir


if __name__ == "__main__":
    archiver_anciens_fichiers()
