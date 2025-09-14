#!/bin/bash
set -e

# Farben
GREEN='\033[1;32m'
BLUE='\033[1;34m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} Starte EchoCloud..."

source venv/bin/activate

python3.12 main.py

echo -e "${GREEN}[ERFOLG]${NC} EchoCloud wurde beendet."
