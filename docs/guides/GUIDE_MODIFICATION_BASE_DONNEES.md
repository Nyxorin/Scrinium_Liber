# 📝 Guide de Modification de la Base de Données

**Pour utilisateurs de Numbers (macOS)**

---

## 📄 Fichier Principal à Modifier

### Fichier de la Base de Données

```
ebook_organizer/validation_humaine.csv
```

**Chemin complet :**
```
/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_humaine.csv
```

---

## 🚀 Workflow de Modification avec Numbers

### Étape 1 : Ouvrir le Fichier avec Numbers

```bash
# Depuis le Terminal
open "ebook_organizer/validation_humaine.csv"

# Ou depuis le Finder
Double-cliquer sur validation_humaine.csv
```

**Résultat :** Numbers s'ouvre automatiquement avec votre fichier.

---

### Étape 2 : Faire vos Modifications

Dans Numbers, vous pouvez modifier :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **Fichier** | Nom du fichier ebook | "Mon livre.epub" |
| **Titre** | Titre du livre | "Le Seigneur des Anneaux" |
| **Auteur(s)** | Nom de l'auteur | "Tolkien, J.R.R." |
| **Nationalité(s)** | Nationalité | "Royaume-Uni" |
| **Date naissance** | Année de naissance | "1892" |
| **Date décès** | Année de décès | "1973" |

**⚠️ IMPORTANT :** Ne modifiez PAS la structure (ordre des colonnes, noms des colonnes).

---

### Étape 3 : Enregistrer (⌘S)

Numbers va créer/mettre à jour un fichier `.numbers` :

```
ebook_organizer/validation_humaine.numbers
```

**C'est normal !** Mais ce n'est pas suffisant...

---

### Étape 4 : Exporter en CSV (CRUCIAL !)

**⚠️ ÉTAPE OBLIGATOIRE** pour que les scripts Python puissent lire vos modifications.

#### Dans Numbers :

1. `Fichier` → `Exporter vers` → `CSV...`

   **Raccourci clavier :** `⌥⇧⌘E` (Option + Shift + Cmd + E)

2. **Paramètres d'export (IMPORTANT) :**
   ```
   ┌────────────────────────────────────────┐
   │  Exporter en CSV                       │
   ├────────────────────────────────────────┤
   │                                        │
   │  Encodage texte : [Unicode (UTF-8) ▼] │  ← OBLIGATOIRE
   │                                        │
   │  Séparateur :     [Point-virgule   ▼] │  ← OBLIGATOIRE
   │                                        │
   │  ☑ Inclure l'en-tête                  │  ← OBLIGATOIRE
   │                                        │
   │  [Annuler]              [Suivant ›]   │
   └────────────────────────────────────────┘
   ```

3. **Enregistrer en écrasant le fichier CSV original**

   Nom du fichier : `validation_humaine.csv`

   **Emplacement :** `ebook_organizer/`

4. Si Numbers demande confirmation, cliquer **"Remplacer"**

---

### Étape 5 : Fermer Numbers

Votre base de données est maintenant mise à jour ! ✅

---

## 📋 Résumé Rapide

```
1. Ouvrir : validation_humaine.csv (double-clic)
   ↓
2. Modifier : dans Numbers (comme Excel)
   ↓
3. Sauvegarder : ⌘S (crée un fichier .numbers)
   ↓
4. Exporter : ⌥⇧⌘E → CSV (point-virgule, UTF-8)
   ↓
5. Remplacer : validation_humaine.csv
   ↓
6. ✅ Terminé !
```

---

## ⚠️ Erreurs Courantes à Éviter

### ❌ Erreur #1 : Oublier d'Exporter en CSV

**Problème :**
- Vous sauvegardez en `.numbers` uniquement
- Les scripts Python ne peuvent pas lire les fichiers `.numbers`
- Vos modifications ne sont pas prises en compte

**Solution :**
- **TOUJOURS** exporter en CSV après avoir sauvegardé

---

### ❌ Erreur #2 : Mauvais Séparateur

**Problème :**
- Vous exportez avec une virgule comme séparateur
- Le fichier devient illisible pour les scripts

**Solution :**
- Utiliser **Point-virgule** comme séparateur (obligatoire)

---

### ❌ Erreur #3 : Mauvais Encodage

**Problème :**
- Vous exportez en ISO-8859 ou autre
- Les accents deviennent bizarres (é → Ã©)

**Solution :**
- Utiliser **Unicode (UTF-8)** comme encodage (obligatoire)

---

## 🔍 Vérification

Pour vérifier que votre modification a bien été prise en compte :

```bash
# Vérifier qu'un titre a été modifié
grep "Mon Titre Modifié" ebook_organizer/validation_humaine.csv
```

Si vous voyez votre modification, c'est bon ! ✅

---

## 🛡️ Sécurité

### Backup Automatique

Avant toute modification importante, créez une copie :

```bash
cp ebook_organizer/validation_humaine.csv ebook_organizer/validation_humaine_backup_$(date +%Y%m%d).csv
```

### Ou utilisez le script Python

Le script `appliquer_validations.py` crée automatiquement un backup avant toute modification.

---

## 📊 Structure du Fichier

### Colonnes Importantes

| Colonne | Type | Obligatoire | Exemple |
|---------|------|-------------|---------|
| **Fichier** | Texte | ✅ Oui | "Mon livre.epub" |
| **Titre** | Texte | ✅ Oui | "Le Seigneur des Anneaux" |
| **Auteur(s)** | Texte | ✅ Oui | "Tolkien, J.R.R." |
| Nationalité(s) | Texte | ❌ Non | "Royaume-Uni" |
| Date naissance | Année | ❌ Non | "1892" |
| Date décès | Année | ❌ Non | "1973" |
| Siècle(s) | Texte | ❌ Non | "19;20" |
| Description | Texte | ❌ Non | "écrivain britannique" |
| Source | Texte | ❌ Non | "BnF" |

**⚠️ Les 3 premières colonnes (Fichier, Titre, Auteur) sont OBLIGATOIRES.**

---

## 💡 Conseils de Modification

### Format des Auteurs

**Toujours utiliser le format :** `Nom, Prénom`

```
✅ Correct :
- "Tolkien, J.R.R."
- "Hugo, Victor"
- "Rowling, J.K."

❌ Incorrect :
- "J.R.R. Tolkien"
- "Victor Hugo"
```

### Format des Titres

**Commencer par une majuscule, respecter les articles :**

```
✅ Correct :
- "Le Seigneur des Anneaux"
- "L'Étranger"
- "Les Misérables"

❌ Incorrect :
- "le seigneur des anneaux"
- "Étranger, L'"
- "Misérables, Les"
```

### Séries et Tomes

**Format recommandé :**

```
✅ "Harry Potter et la pierre philosophale"
✅ "Harry Potter, Tome 1"
✅ "Le Seigneur des Anneaux, T1"
```

---

## 🔄 Workflow Complet Illustré

### Scénario : Corriger le titre d'un livre

```
1. Ouvrir validation_humaine.csv
   ↓
   Numbers s'ouvre

2. Trouver la ligne du livre
   ↓
   Utiliser ⌘F pour chercher

3. Modifier le titre
   ↓
   Clic sur la cellule, taper le nouveau titre

4. Sauvegarder (⌘S)
   ↓
   Numbers crée validation_humaine.numbers

5. Exporter en CSV (⌥⇧⌘E)
   ↓
   Séparateur : Point-virgule
   Encodage : UTF-8

6. Remplacer validation_humaine.csv
   ↓
   Cliquer "Remplacer"

7. ✅ Modification appliquée !
```

---

## 🆘 Dépannage

### Problème : "Numbers ne s'ouvre pas"

**Solution 1 :** Forcer l'ouverture avec Numbers
```bash
open -a Numbers "ebook_organizer/validation_humaine.csv"
```

**Solution 2 :** Importer dans Numbers
- Ouvrir Numbers
- Fichier → Ouvrir
- Sélectionner validation_humaine.csv

---

### Problème : "Mes modifications ne sont pas prises en compte"

**Cause probable :** Vous avez oublié d'exporter en CSV

**Solution :**
1. Rouvrir le fichier `.numbers`
2. Fichier → Exporter vers → CSV
3. Séparateur : Point-virgule
4. Remplacer validation_humaine.csv

---

### Problème : "Les accents sont bizarres"

**Cause :** Mauvais encodage lors de l'export

**Solution :**
- Réexporter en choisissant **Unicode (UTF-8)**

---

## 📁 Fichiers Associés

| Fichier | Description | À Modifier ? |
|---------|-------------|--------------|
| `validation_humaine.csv` | ✅ **Base de données principale** | **OUI - C'est celui-ci !** |
| `validation_humaine.numbers` | Fichier Numbers (créé auto) | Non (intermédiaire) |
| `validation_humaine_backup_*.csv` | Backups automatiques | Non (sécurité) |

---

## 🎯 Checklist de Modification

Avant de fermer Numbers :

- [ ] J'ai fait mes modifications
- [ ] J'ai sauvegardé (⌘S)
- [ ] **J'ai exporté en CSV** (⌥⇧⌘E)
- [ ] J'ai choisi **Point-virgule** comme séparateur
- [ ] J'ai choisi **UTF-8** comme encodage
- [ ] J'ai **remplacé** validation_humaine.csv
- [ ] J'ai vérifié que mes modifications sont présentes

**Si toutes les cases sont cochées, c'est bon !** ✅

---

## 📚 Documentation Complémentaire

- [DEMARRAGE_RAPIDE_NUMBERS.md](DEMARRAGE_RAPIDE_NUMBERS.md) - Guide Numbers pour validation
- [README.md](README.md) - Documentation principale du projet

---

## 🎉 Résumé Ultra-Rapide

### Le Fichier à Modifier

```
ebook_organizer/validation_humaine.csv
```

### Les Étapes

```
1. Double-cliquer sur validation_humaine.csv
2. Modifier dans Numbers
3. Sauvegarder (⌘S)
4. Exporter CSV (⌥⇧⌘E) avec point-virgule + UTF-8
5. Remplacer validation_humaine.csv
```

### Les Paramètres Obligatoires

```
✅ Séparateur : Point-virgule
✅ Encodage : UTF-8
✅ Inclure l'en-tête
```

---

**C'est tout ! Simple et efficace.** 🚀

**Date :** 2025-11-12
**Version :** 1.0
