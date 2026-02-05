#!/bin/bash
# Script d'installation automatique pour EPUB Cleaner
# Ce script crée un environnement virtuel et installe toutes les dépendances

set -e  # Arrêter en cas d'erreur

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         📚 EPUB Cleaner - Installation                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo ""

# Resolve Project Root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_ROOT"

# Vérifier que Python 3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    echo "   Installez Python 3.7 ou supérieur avant de continuer"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Python détecté: $PYTHON_VERSION"
echo ""

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
else
    echo "✓ Environnement virtuel existe déjà"
fi
echo ""

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate
echo "✓ Environnement virtuel activé"
echo ""

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip --quiet
echo "✓ pip mis à jour"
echo ""

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt
echo "✓ Dépendances installées"
echo ""

# Vérifier l'installation
echo "🧪 Vérification de l'installation..."
python -c "import ebooklib; import bs4; print('✓ ebooklib: importé avec succès'); print('✓ beautifulsoup4:', bs4.__version__)"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         ✅ Installation terminée avec succès !                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Pour utiliser EPUB Cleaner:"
echo ""
echo "1️⃣  Activer l'environnement virtuel:"
echo "    source venv/bin/activate"
echo ""
echo "2️⃣  Tester l'installation:"
echo "    python test_cleaner.py"
echo ""
echo "3️⃣  Nettoyer un EPUB:"
echo "    python epub_cleaner.py input.epub output.epub"
echo ""
echo "4️⃣  Désactiver l'environnement virtuel (quand vous avez fini):"
echo "    deactivate"
echo ""
