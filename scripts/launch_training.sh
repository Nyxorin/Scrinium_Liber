#!/bin/bash

# Scrinium Liber - Intensive Training Launcher
echo "--------------------------------------------------"
echo "   Scrinium Liber - Deep Learning Session (8h+)   "
echo "--------------------------------------------------"


# Resolve Project Root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_ROOT"

# Ensure logs directory exists
mkdir -p data/logs

# Kill any existing defender daemons to start fresh
pkill -f "defender_daemon.py" 2>/dev/null

# Run the training in background with nohup so it doesn't stop if terminal closes
echo "🚀 Starting session in background..."
nohup python3 tools/run_intensive_session.py > data/logs/current_session.log 2>&1 &

echo "✅ Session launched with PID $!"
echo "📜 You can follow the progress with: tail -f data/logs/current_session.log"
echo "--------------------------------------------------"
