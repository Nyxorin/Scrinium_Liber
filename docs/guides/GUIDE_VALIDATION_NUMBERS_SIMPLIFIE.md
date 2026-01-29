# 📊 Guide Simplifié - Validation avec Numbers

## ✅ Solution Simple et Fiable

Au lieu de convertir automatiquement (qui peut être lent), voici la méthode la plus simple pour travailler avec Numbers.

---

## 🚀 Méthode Recommandée (3 étapes)

### Étape 1 : Valider dans Numbers

1. **Double-cliquez** sur le fichier CSV dans le Finder
2. Numbers s'ouvre automatiquement
3. **Remplissez la colonne ACTION** :
   - Laissez **VIDE** pour accepter ✅
   - Écrivez **X** pour rejeter ❌

**Exemple :**
```
Ligne 1 : Vide    → Accepter l'inversion
Ligne 2 : X       → Rejeter (garder tel quel)
Ligne 3 : Vide    → Accepter
```

---

### Étape 2 : Exporter en CSV depuis Numbers

**Très important !** Quand vous avez fini de valider :

1. Dans Numbers : `Fichier` → `Exporter vers` → `CSV...`

   ![Export CSV](https://i.imgur.com/numbers-export.png)

2. **Paramètres d'export :**
   - Encodage texte : **Unicode (UTF-8)** ✅
   - Séparateur : **Point-virgule** ✅ (Important !)

3. **Enregistrer** en écrasant le fichier CSV original

**Raccourci clavier :**
- `⌥⇧⌘E` (Option + Shift + Cmd + E) → Export CSV

---

### Étape 3 : Appliquer les Validations

Une fois tous vos fichiers CSV exportés depuis Numbers :

```bash
cd "/Users/parisis/kDrive/Python Projets/Scrinium_Liber"
python3 appliquer_inversions_validees_amelioree.py
```

Le script va :
- ✅ Lire tous les CSV du dossier `validation_amelioree/`
- ✅ Analyser vos validations (colonne ACTION)
- ✅ Créer un backup automatique
- ✅ Appliquer les inversions approuvées

---

## 📋 Workflow Complet

### Fichier par Fichier

Pour chaque fichier de validation :

```bash
# 1. Ouvrir avec Numbers
open "ebook_organizer/validation_amelioree/validation_certaines_100+.csv"

# 2. Dans Numbers :
#    - Remplir la colonne ACTION
#    - Fichier → Exporter vers → CSV
#    - Séparateur : Point-virgule ✅
#    - Enregistrer (écrase le CSV original)

# 3. Répéter pour les autres fichiers (si souhaité)

# 4. Quand tous les fichiers sont validés et exportés :
python3 appliquer_inversions_validees_amelioree.py
```

---

## 💡 Pourquoi Exporter en CSV ?

### Le Format .numbers vs .csv

| Format | Avantage | Inconvénient |
|--------|----------|--------------|
| `.numbers` | Natif macOS, formatage riche | Non lisible par Python ❌ |
| `.csv` | Lisible par Python ✅ | Pas de formatage |

**Solution :** Travailler dans Numbers, mais **exporter en CSV** pour que Python puisse lire.

---

## 🎯 Paramètres d'Export Importants

### Dans Numbers : Fichier → Exporter vers → CSV

**Paramètres OBLIGATOIRES :**

```
┌────────────────────────────────────────┐
│  Exporter en CSV                       │
├────────────────────────────────────────┤
│                                        │
│  Encodage texte : [Unicode (UTF-8) ▼] │  ← IMPORTANT
│                                        │
│  Séparateur :     [Point-virgule   ▼] │  ← TRÈS IMPORTANT
│                                        │
│  ☑ Inclure l'en-tête                  │  ← IMPORTANT
│                                        │
│  [Annuler]              [Suivant ›]   │
└────────────────────────────────────────┘
```

**Si vous oubliez ces paramètres, le script ne pourra pas lire le fichier !**

---

## 🔍 Exemple Complet

### Fichier : validation_certaines_100+.csv

#### 1. Ouvrir

```bash
open "ebook_organizer/validation_amelioree/validation_certaines_100+.csv"
```

Numbers affiche :

| ID | Fichier | Titre_actuel | Auteur_actuel | ACTION | Score |
|----|---------|--------------|---------------|--------|-------|
| 1 | Crime... | Wilde, Oscar | Crime... | | 125 |
| 2 | Peste... | Camus, Albert | Peste, La | | 180 |
| 3 | Raffles... | Ryû, Murakami | Raffles | | 90 |

#### 2. Valider

Remplir la colonne ACTION :

| ID | Fichier | Titre_actuel | Auteur_actuel | **ACTION** | Score |
|----|---------|--------------|---------------|------------|-------|
| 1 | Crime... | Wilde, Oscar | Crime... | | 125 |
| 2 | Peste... | Camus, Albert | Peste, La | | 180 |
| 3 | Raffles... | Ryû, Murakami | Raffles | **X** | 90 |

**Décisions :**
- Ligne 1 : Vide → Accepter ✅
- Ligne 2 : Vide → Accepter ✅
- Ligne 3 : X → Rejeter ❌

#### 3. Exporter

1. `Fichier` → `Exporter vers` → `CSV`
2. Séparateur : **Point-virgule**
3. Encodage : **UTF-8**
4. Enregistrer → **Écraser** le fichier CSV original

#### 4. Appliquer

```bash
python3 appliquer_inversions_validees_amelioree.py
```

---

## ⚡ Raccourcis Clavier Numbers

Pour aller plus vite :

| Action | Raccourci |
|--------|-----------|
| **Passer à la cellule suivante** | `Tab` |
| **Passer à la ligne suivante** | `↓` ou `Entrée` |
| **Exporter en CSV** | `⌥⇧⌘E` |
| **Sauvegarder** | `⌘S` |
| **Fermer** | `⌘W` |

---

## 🆘 Dépannage

### Problème : "Le script ne détecte pas mes validations"

**Cause probable :** Vous avez sauvegardé en `.numbers` au lieu d'exporter en `.csv`

**Solution :**
1. Rouvrir le fichier `.numbers`
2. `Fichier` → `Exporter vers` → `CSV`
3. **Écraser** le fichier CSV original

### Problème : "Erreur de lecture CSV"

**Cause probable :** Mauvais séparateur

**Solution :**
Lors de l'export depuis Numbers, choisir **Point-virgule** comme séparateur.

### Problème : "Caractères bizarres (é → Ã©)"

**Cause probable :** Mauvais encodage

**Solution :**
Lors de l'export depuis Numbers, choisir **Unicode (UTF-8)**.

---

## 📊 Stratégies de Validation

### Option 1 : Rapide (1-2h) ⭐ RECOMMANDÉ

```
✅ validation_certaines_100+.csv (2 369 cas)
   → 99% de précision
   → Validation rapide (beaucoup d'évidences)
```

**Temps :**
- Validation dans Numbers : 1h
- Export : 30 secondes
- Application : 5 minutes

### Option 2 : Optimale (3-4h)

```
✅ validation_certaines_100+.csv (2 369 cas)
✅ validation_haute_90-94.csv (1 489 cas)
   → 97% de précision
```

**Temps :**
- Validation dans Numbers : 3-4h
- Export : 1 minute
- Application : 5 minutes

### Option 3 : Maximale (6-8h)

```
✅ Tous les fichiers (4 169 cas)
   → 96% de précision
```

---

## 📝 Checklist

### Pour Chaque Fichier

- [ ] Ouvrir le CSV avec Numbers (double-clic)
- [ ] Remplir la colonne ACTION (vide = OK, X = rejeter)
- [ ] **Exporter en CSV** : `Fichier` → `Exporter vers` → `CSV`
  - [ ] Séparateur : Point-virgule
  - [ ] Encodage : UTF-8
  - [ ] Écraser le fichier original
- [ ] Fermer Numbers

### Une Fois Tous les Fichiers Validés

- [ ] Exécuter `python3 appliquer_inversions_validees_amelioree.py`
- [ ] Vérifier le résumé
- [ ] Confirmer avec `o`
- [ ] Vérifier le backup créé
- [ ] Consulter le rapport généré

---

## 🎯 Résumé Ultra-Rapide

```bash
# 1. Valider dans Numbers
open "ebook_organizer/validation_amelioree/validation_certaines_100+.csv"
# Remplir ACTION : vide = OK, X = rejeter

# 2. Exporter en CSV
# Fichier → Exporter vers → CSV (point-virgule, UTF-8)

# 3. Appliquer
python3 appliquer_inversions_validees_amelioree.py
```

**L'étape 2 (export CSV) est CRUCIALE !**

---

## 💻 Script Compatible

Le script `appliquer_inversions_validees_amelioree.py` :
- ✅ Lit tous les CSV du dossier `validation_amelioree/`
- ✅ Ignore les fichiers `.numbers` (lit seulement les `.csv`)
- ✅ Crée un backup automatique
- ✅ Génère un rapport détaillé

---

**Date :** 2025-11-12
**Méthode :** Validation Numbers + Export CSV manuel
