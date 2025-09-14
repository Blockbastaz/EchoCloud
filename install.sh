#!/bin/bash
set -e  # Bei Fehler abbrechen

# Farben (ähnlich Batch-Script, aber mit farbigen Status-Labels)
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
RED='\033[1;31m'
BLUE='\033[1;34m'
NC='\033[0m'

info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}
error() {
  echo -e "${RED}[FEHLER]${NC} $1"
}
success() {
  echo -e "${GREEN}[ERFOLG]${NC} $1"
}
warn() {
  echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

# System aktualisieren
info "System wird aktualisiert..."
# Für Entwicklungszwecke kurzzeitig deaktiviert
# sudo apt update && sudo apt upgrade -y

# Benötigt für mysqlclient
sudo apt install default-libmysqlclient-dev build-essential

# Python3 & Pakete installieren
info "Python3 und wichtige Pakete werden installiert..."
sudo apt install -y python3 python3-venv python3-setuptools curl

# Virtuelle Umgebung erstellen
info "Virtuelle Umgebung wird erstellt..."
python3.12 -m venv venv

# venv aktivieren und pip aktualisieren
info "Virtuelle Umgebung wird aktiviert und pip aktualisiert..."
source venv/bin/activate
pip install --upgrade pip

# requirements installieren
info "Abhängigkeiten aus requirements.txt werden installiert..."
if [[ ! -f requirements.txt ]]; then
  warn "requirements.txt wurde nicht gefunden, überspringe Installation der Abhängigkeiten."
else
  pip install -r requirements.txt
fi

info "Installiere Redis >= 7..."
pip install --upgrade "redis>=7.0.0b1"

success "Installation fertig! EchoCloud wird jetzt gestartet..."
chmod +x run.sh

./run.sh
