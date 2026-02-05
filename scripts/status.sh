#!/bin/bash
# Scrinium Liber - Status Checker

echo "=================================================="
echo "   📊 SCRINIUM LIBER : ÉTAT DU SYSTÈME"
echo "=================================================="
echo "=================================================="

# Resolve Project Root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_ROOT"

echo "📅 Date : $(date)"
echo ""

echo "🔄 [1/3] PROCESSUS D'ENTRAÎNEMENT"
PID=$(pgrep -f "run_intensive_session.py")
if [ -z "$PID" ]; then
    echo "❌ INACTIF (Aucune session en cours)"
else
    echo "✅ ACTIF (PID: $PID)"
    # Show duration if possible (unavailable on minimal ps, skipping for simplicity)
fi
echo "--------------------------------------------------"

echo "🧠 [2/3] INTELLIGENCE (FORGE)"
if [ -f "data/logic_forge_rules.jsonl" ]; then
    COUNT=$(wc -l < data/logic_forge_rules.jsonl)
    echo "💎 Règles Forgées : $COUNT"
    echo "📝 Dernières règles :"
    tail -n 3 data/logic_forge_rules.jsonl
else
    echo "⚠️ Aucune forge trouvée."
fi
echo "--------------------------------------------------"

echo "📜 [3/3] LOGS (5 dernières lignes)"
if [ -f "data/logs/current_session.log" ]; then
    tail -n 5 data/logs/current_session.log
else
    echo "⚠️ Aucun fichier de log trouvé."
fi
echo "=================================================="
echo "💡 Pour voir le log en continu : tail -f data/logs/current_session.log"
