#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse complète des titres des livres dans la base de données
"""

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


def charger_base_donnees(fichier_csv):
    """Charge la base de données et extrait les titres"""

    titres = []

    with open(fichier_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            titre = row.get('Titre', '').strip()
            auteur = row.get('Auteur(s)', '').strip()
            fichier = row.get('Fichier', '').strip()

            if titre:
                titres.append({
                    'titre': titre,
                    'auteur': auteur,
                    'fichier': fichier
                })

    return titres


def analyser_statistiques_base(titres):
    """Statistiques de base sur les titres"""

    stats = {
        'total': len(titres),
        'longueur_moyenne': sum(len(t['titre']) for t in titres) / len(titres) if titres else 0,
        'longueur_min': min(len(t['titre']) for t in titres) if titres else 0,
        'longueur_max': max(len(t['titre']) for t in titres) if titres else 0,
    }

    # Compteurs
    longueurs = [len(t['titre']) for t in titres]
    stats['longueur_mediane'] = sorted(longueurs)[len(longueurs) // 2] if longueurs else 0

    return stats


def analyser_patterns(titres):
    """Analyse des patterns dans les titres"""

    patterns = {
        'avec_virgule': 0,
        'avec_deux_points': 0,
        'avec_tiret': 0,
        'avec_parentheses': 0,
        'avec_chiffres': 0,
        'avec_article_debut': 0,
        'avec_tome': 0,
        'tout_majuscules': 0,
        'commence_majuscule': 0,
    }

    articles = ['Le ', 'La ', 'Les ', "L'", 'Un ', 'Une ', 'Des ']
    mots_tome = ['Tome', 'tome', 'T.', 'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'Vol.', 'Volume']

    for item in titres:
        titre = item['titre']

        if ',' in titre:
            patterns['avec_virgule'] += 1
        if ':' in titre:
            patterns['avec_deux_points'] += 1
        if '-' in titre or '–' in titre or '—' in titre:
            patterns['avec_tiret'] += 1
        if '(' in titre or ')' in titre:
            patterns['avec_parentheses'] += 1
        if re.search(r'\d', titre):
            patterns['avec_chiffres'] += 1
        if any(titre.startswith(art) for art in articles):
            patterns['avec_article_debut'] += 1
        if any(mot in titre for mot in mots_tome):
            patterns['avec_tome'] += 1
        if titre.isupper() and len(titre) > 3:
            patterns['tout_majuscules'] += 1
        if titre and titre[0].isupper():
            patterns['commence_majuscule'] += 1

    return patterns


def detecter_anomalies(titres):
    """Détecte les anomalies dans les titres"""

    anomalies = {
        'tres_courts': [],          # < 3 caractères
        'tres_longs': [],           # > 100 caractères
        'caracteres_suspects': [],  # _, {, }, [, ], etc. dans le titre
        'doubles_espaces': [],      # Espaces multiples
        'commence_minuscule': [],   # Commence par minuscule
        'sans_voyelle': [],         # Pas de voyelles
        'tout_majuscules': [],      # Tout en majuscules
        'caracteres_speciaux': [],  # Caractères non-alphanumériques étranges
    }

    voyelles = 'aeiouyAEIOUYàâäéèêëïîôùûüÿœæ'

    for item in titres:
        titre = item['titre']

        # Très courts
        if len(titre) < 3:
            anomalies['tres_courts'].append(item)

        # Très longs
        if len(titre) > 100:
            anomalies['tres_longs'].append(item)

        # Caractères suspects
        if any(c in titre for c in ['_', '{', '}', '|', '<', '>', '\\', '/']):
            anomalies['caracteres_suspects'].append(item)

        # Doubles espaces
        if '  ' in titre:
            anomalies['doubles_espaces'].append(item)

        # Commence par minuscule
        if titre and titre[0].islower():
            anomalies['commence_minuscule'].append(item)

        # Sans voyelles (au moins 3 consonnes consécutives)
        if not any(v in titre for v in voyelles) and len(titre) > 2:
            anomalies['sans_voyelle'].append(item)

        # Tout en majuscules (titres longs)
        if titre.isupper() and len(titre) > 10:
            anomalies['tout_majuscules'].append(item)

        # Caractères spéciaux étranges
        if re.search(r'[^\w\s\',\.\-:;!?()«»""''\[\]àâäéèêëïîôùûüÿœæçÀÂÄÉÈÊËÏÎÔÙÛÜŸŒÆÇ]', titre):
            anomalies['caracteres_speciaux'].append(item)

    return anomalies


def analyser_articles(titres):
    """Analyse les articles dans les titres"""

    articles_stats = {
        'Le': 0,
        'La': 0,
        'Les': 0,
        "L'": 0,
        'Un': 0,
        'Une': 0,
        'Des': 0,
    }

    articles_fin = []

    for item in titres:
        titre = item['titre']

        # Articles au début
        for article in articles_stats.keys():
            if titre.startswith(article + ' ') or titre.startswith(article):
                articles_stats[article] += 1

        # Articles à la fin (avec virgule)
        if titre.endswith(', Le') or titre.endswith(', La') or titre.endswith(', Les') or titre.endswith(", L'"):
            articles_fin.append(item)

    return articles_stats, articles_fin


def analyser_series(titres):
    """Analyse les séries et tomes"""

    series = []
    pattern_tome = re.compile(r'[Tt]ome?\s*(\d+)|T\.?\s*(\d+)|Vol\.?\s*(\d+)', re.IGNORECASE)

    for item in titres:
        titre = item['titre']

        match = pattern_tome.search(titre)
        if match:
            numero = match.group(1) or match.group(2) or match.group(3)
            series.append({
                'titre': titre,
                'auteur': item['auteur'],
                'numero_tome': numero
            })

    return series


def analyser_ponctuation(titres):
    """Analyse de la ponctuation dans les titres"""

    ponctuation = {
        'virgule': 0,
        'point': 0,
        'deux_points': 0,
        'point_virgule': 0,
        'point_exclamation': 0,
        'point_interrogation': 0,
        'points_suspension': 0,
        'guillemets': 0,
    }

    for item in titres:
        titre = item['titre']

        if ',' in titre:
            ponctuation['virgule'] += 1
        if '.' in titre and not titre.endswith('.'):
            ponctuation['point'] += 1
        if ':' in titre:
            ponctuation['deux_points'] += 1
        if ';' in titre:
            ponctuation['point_virgule'] += 1
        if '!' in titre:
            ponctuation['point_exclamation'] += 1
        if '?' in titre:
            ponctuation['point_interrogation'] += 1
        if '...' in titre or '…' in titre:
            ponctuation['points_suspension'] += 1
        if '"' in titre or '«' in titre or '»' in titre or '"' in titre or '"' in titre:
            ponctuation['guillemets'] += 1

    return ponctuation


def trouver_mots_frequents(titres, top_n=30):
    """Trouve les mots les plus fréquents dans les titres"""

    # Mots à ignorer
    mots_ignores = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'à', 'en', 'au', 'aux', 'dans', 'pour', 'par', 'sur'}

    mots = []

    for item in titres:
        titre = item['titre']
        # Extraire les mots
        mots_titre = re.findall(r'\b[a-zàâäéèêëïîôùûüÿœæ]{3,}\b', titre.lower())
        mots.extend([m for m in mots_titre if m not in mots_ignores])

    return Counter(mots).most_common(top_n)


def generer_rapport(fichier_csv):
    """Génère un rapport complet d'analyse des titres"""

    print("=" * 80)
    print("ANALYSE COMPLÈTE DES TITRES DES LIVRES")
    print("=" * 80)
    print()

    # Charger les données
    print("📚 Chargement de la base de données...")
    titres = charger_base_donnees(fichier_csv)
    print(f"✅ {len(titres)} livres chargés")
    print()

    # Statistiques de base
    print("=" * 80)
    print("📊 STATISTIQUES GÉNÉRALES")
    print("=" * 80)
    stats = analyser_statistiques_base(titres)
    print(f"Total de livres       : {stats['total']}")
    print(f"Longueur moyenne      : {stats['longueur_moyenne']:.1f} caractères")
    print(f"Longueur médiane      : {stats['longueur_mediane']} caractères")
    print(f"Titre le plus court   : {stats['longueur_min']} caractères")
    print(f"Titre le plus long    : {stats['longueur_max']} caractères")
    print()

    # Patterns
    print("=" * 80)
    print("🔍 PATTERNS DANS LES TITRES")
    print("=" * 80)
    patterns = analyser_patterns(titres)
    total = len(titres)
    print(f"Avec virgule(s)       : {patterns['avec_virgule']} ({patterns['avec_virgule']/total*100:.1f}%)")
    print(f"Avec deux-points      : {patterns['avec_deux_points']} ({patterns['avec_deux_points']/total*100:.1f}%)")
    print(f"Avec tiret(s)         : {patterns['avec_tiret']} ({patterns['avec_tiret']/total*100:.1f}%)")
    print(f"Avec parenthèses      : {patterns['avec_parentheses']} ({patterns['avec_parentheses']/total*100:.1f}%)")
    print(f"Avec chiffres         : {patterns['avec_chiffres']} ({patterns['avec_chiffres']/total*100:.1f}%)")
    print(f"Commence par article  : {patterns['avec_article_debut']} ({patterns['avec_article_debut']/total*100:.1f}%)")
    print(f"Contient 'Tome/Vol'   : {patterns['avec_tome']} ({patterns['avec_tome']/total*100:.1f}%)")
    print(f"Tout en MAJUSCULES    : {patterns['tout_majuscules']} ({patterns['tout_majuscules']/total*100:.1f}%)")
    print(f"Commence par majuscule: {patterns['commence_majuscule']} ({patterns['commence_majuscule']/total*100:.1f}%)")
    print()

    # Articles
    print("=" * 80)
    print("📰 ARTICLES DANS LES TITRES")
    print("=" * 80)
    articles_stats, articles_fin = analyser_articles(titres)
    print("Articles au début :")
    for article, count in sorted(articles_stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  • '{article}' : {count} ({count/total*100:.1f}%)")
    print()
    print(f"Articles à la fin (avec virgule) : {len(articles_fin)}")
    if articles_fin:
        print("Exemples :")
        for item in articles_fin[:5]:
            print(f"  • {item['titre']}")
    print()

    # Ponctuation
    print("=" * 80)
    print("✏️ PONCTUATION")
    print("=" * 80)
    ponctuation = analyser_ponctuation(titres)
    print(f"Virgule (,)            : {ponctuation['virgule']} ({ponctuation['virgule']/total*100:.1f}%)")
    print(f"Point (.)              : {ponctuation['point']} ({ponctuation['point']/total*100:.1f}%)")
    print(f"Deux-points (:)        : {ponctuation['deux_points']} ({ponctuation['deux_points']/total*100:.1f}%)")
    print(f"Point-virgule (;)      : {ponctuation['point_virgule']} ({ponctuation['point_virgule']/total*100:.1f}%)")
    print(f"Point d'exclamation (!) : {ponctuation['point_exclamation']} ({ponctuation['point_exclamation']/total*100:.1f}%)")
    print(f"Point d'interrogation (?): {ponctuation['point_interrogation']} ({ponctuation['point_interrogation']/total*100:.1f}%)")
    print(f"Points de suspension   : {ponctuation['points_suspension']} ({ponctuation['points_suspension']/total*100:.1f}%)")
    print(f"Guillemets             : {ponctuation['guillemets']} ({ponctuation['guillemets']/total*100:.1f}%)")
    print()

    # Séries
    print("=" * 80)
    print("📚 SÉRIES ET TOMES")
    print("=" * 80)
    series = analyser_series(titres)
    print(f"Livres faisant partie d'une série : {len(series)} ({len(series)/total*100:.1f}%)")
    if series:
        # Distribution des tomes
        tomes_counter = Counter([int(s['numero_tome']) for s in series if s['numero_tome'].isdigit()])
        print("\nDistribution des numéros de tomes :")
        for tome, count in sorted(tomes_counter.items())[:10]:
            print(f"  • Tome {tome} : {count} livres")
    print()

    # Mots fréquents
    print("=" * 80)
    print("🔤 MOTS LES PLUS FRÉQUENTS DANS LES TITRES")
    print("=" * 80)
    mots_freq = trouver_mots_frequents(titres, top_n=30)
    print("Top 30 des mots (hors articles) :")
    for i, (mot, count) in enumerate(mots_freq, 1):
        print(f"  {i:2d}. {mot:<20} : {count:4d} fois")
    print()

    # Anomalies
    print("=" * 80)
    print("⚠️ ANOMALIES DÉTECTÉES")
    print("=" * 80)
    anomalies = detecter_anomalies(titres)

    print(f"Titres très courts (<3 car.)     : {len(anomalies['tres_courts'])}")
    if anomalies['tres_courts'][:5]:
        print("  Exemples :")
        for item in anomalies['tres_courts'][:5]:
            print(f"    • '{item['titre']}' ({len(item['titre'])} car.)")
    print()

    print(f"Titres très longs (>100 car.)    : {len(anomalies['tres_longs'])}")
    if anomalies['tres_longs'][:3]:
        print("  Exemples :")
        for item in anomalies['tres_longs'][:3]:
            print(f"    • {item['titre'][:80]}... ({len(item['titre'])} car.)")
    print()

    print(f"Avec caractères suspects         : {len(anomalies['caracteres_suspects'])}")
    if anomalies['caracteres_suspects'][:5]:
        print("  Exemples :")
        for item in anomalies['caracteres_suspects'][:5]:
            print(f"    • {item['titre'][:60]}")
    print()

    print(f"Doubles espaces                  : {len(anomalies['doubles_espaces'])}")
    if anomalies['doubles_espaces'][:3]:
        print("  Exemples :")
        for item in anomalies['doubles_espaces'][:3]:
            print(f"    • {item['titre'][:60]}")
    print()

    print(f"Commence par minuscule           : {len(anomalies['commence_minuscule'])}")
    if anomalies['commence_minuscule'][:5]:
        print("  Exemples :")
        for item in anomalies['commence_minuscule'][:5]:
            print(f"    • {item['titre'][:60]}")
    print()

    print(f"Tout en MAJUSCULES (>10 car.)    : {len(anomalies['tout_majuscules'])}")
    if anomalies['tout_majuscules'][:5]:
        print("  Exemples :")
        for item in anomalies['tout_majuscules'][:5]:
            print(f"    • {item['titre'][:60]}")
    print()

    print(f"Caractères spéciaux étranges     : {len(anomalies['caracteres_speciaux'])}")
    if anomalies['caracteres_speciaux'][:5]:
        print("  Exemples :")
        for item in anomalies['caracteres_speciaux'][:5]:
            print(f"    • {item['titre'][:60]}")
    print()

    print("=" * 80)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 80)
    print()

    return {
        'stats': stats,
        'patterns': patterns,
        'anomalies': anomalies,
        'series': series,
        'mots_frequents': mots_freq,
        'ponctuation': ponctuation,
        'articles': articles_stats,
        'articles_fin': articles_fin
    }


def main():
    """Fonction principale"""

    fichier_csv = "/Users/parisis/kDrive/Python Projets/Scrinium_Liber/ebook_organizer/validation_humaine.csv"

    resultat = generer_rapport(fichier_csv)

    print("\n💡 Suggestion : Voulez-vous un rapport détaillé sur une catégorie spécifique ?")
    print("   - Anomalies détaillées")
    print("   - Séries complètes")
    print("   - Titres à corriger")
    print()


if __name__ == "__main__":
    main()
