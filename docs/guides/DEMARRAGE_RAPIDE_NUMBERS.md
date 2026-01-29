# 🚀 Démarrage Rapide - Validation avec Numbers

## ✅ Vous pouvez maintenant travailler avec Numbers !

### Problème résolu
Vous ne pouviez pas modifier les CSV directement. **Solution : utilisez Numbers et exportez en CSV !**

---

## 📋 Checklist en 3 Étapes

### ✅ Étape 1 : Valider dans Numbers

```bash
# Ouvrir un fichier
open "ebook_organizer/validation_amelioree/validation_certaines_100+.csv"
```

**Dans Numbers :**
- Remplissez la colonne **ACTION** :
  - **Vide** = Accepter l'inversion ✅
  - **X** = Rejeter l'inversion ❌

---

### ✅ Étape 2 : Exporter en CSV

**IMPORTANT !** Dans Numbers :

1. `Fichier` → `Exporter vers` → `CSV...`
2. **Séparateur : Point-virgule** (IMPORTANT !)
3. **Encodage : UTF-8**
4. **Enregistrer** (écraser le fichier CSV original)

**Raccourci :** `⌥⇧⌘E` (Option + Shift + Cmd + E)

---

### ✅ Étape 3 : Appliquer les validations

```bash
cd "/Users/parisis/kDrive/Python Projets/Scrinium_Liber"
python3 appliquer_validations.py
```

Le script va :
- ✅ Lire vos fichiers CSV
- ✅ Créer un backup
- ✅ Appliquer les inversions approuvées

---

## 🎯 Workflow Complet

```
1. Double-cliquer sur le CSV
   ↓
2. Numbers s'ouvre
   ↓
3. Remplir la colonne ACTION
   ↓
4. Fichier → Exporter vers → CSV
   (Point-virgule, UTF-8)
   ↓
5. python3 appliquer_validations.py
   ↓
6. ✅ Terminé !
```

---

## ⚡ Fichiers à Valider (par ordre de priorité)

| Fichier | Inversions | Confiance | Temps |
|---------|-----------|-----------|-------|
| **validation_certaines_100+.csv** | 2 369 | 99% | 1-2h |
| **validation_haute_90-94.csv** | 1 489 | 95% | 3-4h |
| validation_moyenne_haute_80-84.csv | 99 | 88% | 30min |
| validation_moyenne_70-74.csv | 144 | 80% | 45min |
| validation_basse_60-69.csv | 68 | 75% | 30min |

**Conseil :** Commencez par les 2 premiers fichiers (Option 2 : Optimale)

---

## 💡 Points Importants

### ✅ À Faire
- Exporter en CSV depuis Numbers avant d'exécuter le script
- Utiliser **point-virgule** comme séparateur
- Utiliser **UTF-8** comme encodage

### ❌ À Ne Pas Faire
- Sauvegarder uniquement en `.numbers` (le script ne peut pas les lire)
- Utiliser virgule comme séparateur
- Oublier d'exporter après modification

---

## 🆘 En Cas de Problème

### "Le script ne trouve pas mes validations"

**Solution :** Vous avez oublié d'exporter en CSV
1. Rouvrir le fichier `.numbers`
2. `Fichier` → `Exporter vers` → `CSV`
3. Point-virgule + UTF-8
4. Écraser le CSV original

### "Erreur de lecture CSV"

**Solution :** Mauvais séparateur
- Lors de l'export, choisir **point-virgule**

---

## 📚 Documentation Complète

- [GUIDE_VALIDATION_NUMBERS_SIMPLIFIE.md](GUIDE_VALIDATION_NUMBERS_SIMPLIFIE.md) - Guide complet
- [GUIDE_VALIDATION_AMELIOREE.md](GUIDE_VALIDATION_AMELIOREE.md) - Stratégies de validation
- [EXPLICATION_METHODE_AMELIOREE.md](EXPLICATION_METHODE_AMELIOREE.md) - Explications techniques

---

## 🎯 Commandes Essentielles

```bash
# Ouvrir un fichier avec Numbers
open "ebook_organizer/validation_amelioree/validation_certaines_100+.csv"

# Appliquer les validations
python3 appliquer_validations.py

# Vérifier les fichiers disponibles
ls -lh "ebook_organizer/validation_amelioree/"
```

---

**C'est parti ! Commencez par le premier fichier (certaines) pour des résultats rapides !** 🚀

**Date :** 2025-11-12
