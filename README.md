# EPUB Cleaner - Nettoyeur d'erreurs OCR pour EPUB

Outil Python pour nettoyer et réparer les fichiers EPUB contenant des erreurs OCR.

## Fonctionnalités

### Corrections automatiques

1. **Caractères spéciaux mal interprétés**
   - `˚` → `û` (d˚ → dû, s˚r → sûr)
   - `‚` → `â` (verd‚tres → verdâtres)
   - `˘` → `ù` (o˘ → où)
   - Et de nombreux autres caractères courants

2. **Césures en fin de ligne**
   - `voi-\ntures` → `voitures`
   - Supprime les coupures de mots inappropriées

3. **Espaces multiples**
   - `avai     le` → `avai le`
   - Normalise les espaces excessifs

4. **Mots collés**
   - `quequelques` → `que quelques`
   - Détecte et sépare les mots fusionnés

5. **Mots courants mal reconnus**
   - `fis` → `ils`
   - Dictionnaire personnalisable

## Installation

```bash
# Cloner ou télécharger ce dépôt
cd Scrinium_Liber

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Mode automatique (RECOMMANDÉ)

**Le moyen le plus simple d'utiliser Scrinium_Liber !**

```bash
# Placer vos EPUBs dans livres_originaux/
# Les fichiers nettoyés apparaîtront dans livres_traites/
python auto_cleaner.py
```

**Mode surveillance (automatique continu):**
```bash
# Nettoie automatiquement chaque nouveau fichier détecté
python auto_cleaner.py --watch
```

📖 **Voir le [Guide Auto Cleaner](GUIDE_AUTO_CLEANER.md) pour plus de détails**

### Mode ligne de commande (fichier unique)

```bash
python epub_cleaner.py input.epub output_cleaned.epub
```

### Mode batch (plusieurs fichiers)

```bash
# Nettoyer tous les EPUBs d'un répertoire
python batch_cleaner.py "*.epub" livres_nettoyes
```

### Mode programmatique

```python
from epub_cleaner import EPUBCleaner

cleaner = EPUBCleaner('mon_livre.epub')
cleaner.clean('mon_livre_clean.epub')
```

### Test sur l'extrait d'exemple

```bash
python test_cleaner.py
```

Ce script teste le nettoyeur sur l'extrait fourni et affiche les corrections appliquées.

## Structure du projet

```
Scrinium_Liber/
├── auto_cleaner.py              # 🆕 Script de nettoyage automatique (RECOMMANDÉ)
├── epub_cleaner.py              # Module principal
├── batch_cleaner.py             # Traitement par lots
├── test_cleaner.py              # Script de test
├── requirements.txt             # Dépendances Python
├── livres_originaux/            # 🆕 Répertoire d'entrée (créé automatiquement)
├── livres_traites/              # 🆕 Répertoire de sortie (créé automatiquement)
├── README.md                    # Documentation principale
├── GUIDE_AUTO_CLEANER.md        # 🆕 Guide du mode automatique
└── GUIDE_DEMARRAGE.md           # Guide de démarrage
```

## Architecture

### Classe `OCRCleaner`

Responsable du nettoyage du texte brut. Contient :

- `char_replacements` : Dictionnaire de remplacement de caractères
- `regex_patterns` : Liste de patterns regex pour corrections
- `clean_special_chars()` : Remplace les caractères spéciaux
- `apply_regex_corrections()` : Applique les regex
- `fix_common_ocr_words()` : Corrige les mots fréquents
- `clean_text()` : Pipeline complet

### Classe `EPUBCleaner`

Gère la manipulation des fichiers EPUB. Contient :

- `load_epub()` : Charge le fichier EPUB
- `clean_html_content()` : Nettoie le HTML d'un chapitre
- `process_epub()` : Traite tous les chapitres
- `save_epub()` : Sauvegarde l'EPUB nettoyé
- `clean()` : Pipeline complet

## Personnalisation

### Ajouter des caractères à corriger

Éditez le dictionnaire `char_replacements` dans [epub_cleaner.py](epub_cleaner.py:15) :

```python
self.char_replacements = {
    '˚': 'û',
    '‚': 'â',
    # Ajoutez vos propres mappings ici
    'Ø': 'œ',
}
```

### Ajouter des corrections regex

Ajoutez des tuples (pattern, remplacement) dans [epub_cleaner.py](epub_cleaner.py:42) :

```python
self.regex_patterns = [
    (r'quequelques', 'que quelques'),
    # Ajoutez vos patterns ici
    (r'\bvotre_pattern\b', 'remplacement'),
]
```

### Ajouter des mots à corriger

Modifiez le dictionnaire dans [epub_cleaner.py](epub_cleaner.py:75) :

```python
word_corrections = {
    'fis': 'ils',
    'avai': 'avait',
    # Ajoutez vos corrections
    'inais': 'mais',
}
```

## Limitations actuelles

1. **Texte corrompu sévèrement** : Les passages complètement illisibles (ex: "en Ô Jf") ne peuvent pas être automatiquement corrigés
2. **Contexte** : L'outil ne comprend pas le contexte, certaines corrections peuvent être inappropriées
3. **Noms propres** : Peut mal corriger des noms propres étrangers
4. **Images** : Ne traite pas les images contenant du texte

## Améliorations futures

- [ ] Intégration de SymSpell pour correction orthographique avancée
- [ ] Support de LanguageTool pour grammaire
- [ ] Détection automatique de la langue
- [ ] Interface graphique
- [ ] Traitement batch de plusieurs EPUB
- [ ] Rapport détaillé des corrections
- [ ] Mode interactif pour validation manuelle

## Dépendances

- `ebooklib` : Manipulation d'EPUB
- `beautifulsoup4` : Parsing HTML
- `lxml` : Parser XML performant

## Licence

Open source - À définir

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ajouter des mappings de caractères
- Améliorer les regex
- Proposer de nouvelles fonctionnalités

## Support

Pour signaler un problème ou demander une fonctionnalité, créez une issue.
