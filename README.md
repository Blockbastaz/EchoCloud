
---

<p align="center">
  <img src="https://github.com/Blockbastaz/EchoCloud/blob/main/data/logo.png" alt="EchoCloud Logo" width="200"/>
</p>

<h1 align="center">EchoCloud</h1>

<p align="center">
  <strong>Ein modernes, modulares Server-Management-System für Minecraft-Infrastrukturen mit integrierter API und persistenter Speicherung.</strong><br/>
  <em>Effizient. Sicher. Erweiterbar.</em>
</p>

---

## Übersicht

**EchoCloud** ist ein Python-basiertes CLI- und API-System zur Verwaltung mehrerer Minecraft-Serverinstanzen. Es bietet zentrale Kontrolle, Echtzeitüberwachung und sichere Kommunikation über REST-APIs und WebSockets.

---

## Hauptfunktionen

* **Multi-Server-Verwaltung**: Zentrale Kontrolle über mehrere Minecraft-Serverinstanzen
* **RESTful API**: Sicheres HTTPS-API mit Token-Authentifizierung
* **WebSocket-Support**: Echtzeit-Kommunikation in beide Richtungen
* **Persistente Speicherung**: MySQL, MariaDB, PostgreSQL oder H2
* **Auto-Discovery**: Automatische Servererkennung und -registrierung
* **Screen-Integration**: Nahtlose Verwaltung von Linux-Screen-Sessions
* **Rich CLI**: Interaktive Kommandozeile mit Syntax-Highlighting
* **SSL/TLS-Unterstützung**: Automatische Zertifikatserstellung für sichere Kommunikation

---

## Architektur

```
EchoCloud/
├── core/                   # Kernmodule
│   ├── server_manager.py   # Server Lifecycle Management
│   ├── console.py          # CLI Utilities & Formatierung
│   └── certgen.py          # SSL-Zertifikatserstellung
├── commands/               # Kommando-System
│   └── commandmanager.py   # CLI-Dispatcher
├── api/                    # API-Ebene
│   └── apimanager.py       # FastAPI-Server & WebSocket-Handler
├── utils/                  # Hilfsfunktionen
│   └── storagemanager.py   # Datenbankabstraktion
└── config/                 # Konfigurationsdateien
    └── settings.yaml       # Hauptkonfiguration
```

---

## Voraussetzungen

* **Python 3.8+**
* **Linux/Unix**
* **Java** 

---

## Installation

1. Repository klonen:

```bash
git clone https://github.com/yourusername/EchoCloud.git
cd EchoCloud
```

2. Installationsskript ausführbar machen:

```bash
chmod +x install.sh
```

3. Installation starten:

```bash
./install.sh
```

4. Server Importieren:

```bash
autoscan
```

> Hinweis: Das Skript installiert notwendige Python-Abhängigkeiten und legt die Standardverzeichnisse für Server und Datenbanken an.

---

## Konfiguration

Bearbeite die Datei `config/settings.yaml`:

```yaml
server:
  default_path: "../Cloud/running/static"
  version: "paper-1.21.1-133.jar"
  check_delay: 10            # Zeit (in Sekunden), um den Serverstatus nach Start zu prüfen

cloud:
  autoregister: true         # Server aus Standardpfad automatisch registrieren
  debug_mode: false          # Entwicklernachrichten aktivieren
  host: "localhost"          # EchoCloud-Adresse
  port: 9989                 # EchoCloud-Port

network:
  use_https: true            # HTTPS für Serverkommunikation aktivieren
  auto_cert: true            # Zertifikat automatisch generieren
  auto_api: false            # API automatisch beim Start aktivieren
  cert_duration_days: 365    # Gültigkeitsdauer des Zertifikats
  auth_config_path: "./config/auth_tokens.yaml"
  cert_file_path: "./config/cert.pem"
  key_file_path: "./config/key.pem"

storage:
  storage_type: "h2"          # Optionen: "mysql", "mariadb", "postgresql", "h2"
  host: "localhost"           # Datenbankhost (nur bei MySQL/MariaDB/PostgreSQL)
  port: 3306                  # Standardports: MySQL/MariaDB: 3306, PostgreSQL: 5432
  username: "root"            # Datenbankbenutzer
  password: "passwort"        # Datenbankpasswort
  database: "EchoCloud"       # Datenbankname
  table_name: "json_storage"  # Tabelle für EchoCloud-Daten
  h2_file_path: "data/"       # Pfad zur H2-Datei
```

---

## Nutzung

### CLI starten

```bash
python main.py
```

#### Kernkommandos

| Befehl            | Beschreibung                      | Beispiel         |
|-------------------|-----------------------------------| ---------------- |
| `servers`         | Liste aller registrierten Server  | `servers`        |
| `select <server>` | Server für Operationen auswählen  | `select Lobby-1` |
| `status`          | Detaillierter Serverstatus        | `status`         |
| `start`           | Ausgewählten Server starten       | `start`          |
| `stop`            | Ausgewählten Server stoppen       | `stop`           |
| `logs`            | Server-Logs anzeigen              | `logs`           |
| `autoscan`        | Neue Server automatisch scannen   | `autoscan`       |
| `startapi`        | API-Webserver starten             | `startapi`       |
| `debug`           | Debug-Modus ein-/ausschalten      | `debug`          |
| `help`            | Alle verfügbaren Befehle anzeigen | `help`           |
| `exit`            | EchoCloud Stoppen                 | `help`           |

---

### API Nutzung

#### Authentifizierung

Jeder Server hat ein eigenes Token in `config/auth_tokens.yaml`. Tokens werden bei der Registrierung automatisch erstellt.

#### REST API Beispiel

```http
POST /api/plugin/{server_id}/{auth_token}
Content-Type: application/json

{
  "playerName": "Steve",
  "action": "jump",
  "data": {}
}
```

#### WebSocket Beispiel

```javascript
const ws = new WebSocket('wss://localhost:9989/ws/server_id/auth_token');

ws.send(JSON.stringify({
  "type": "command",
  "data": "say Hallo Welt"
}));
```

#### Health Check

```http
GET /api/ping
```

---

## Datenbankunterstützung

### H2 (Standard)

Leichtgewichtige, dateibasierte Datenbank – ideal für Entwicklung:

```yaml
storage:
  storage_type: "h2"
  h2_file_path: "data/"
```

### MySQL/MariaDB

Produktionsreife relationale Datenbank:

```yaml
storage:
  storage_type: "mysql"  # oder "mariadb"
  host: "localhost"
  port: 3306
  username: "echocloud"
  password: "secure_password"
  database: "echocloud_db"
```

### PostgreSQL

Leistungsstarke Datenbank für große Installationen:

```yaml
storage:
  storage_type: "postgresql"
  host: "localhost"
  port: 5432
  username: "echocloud"
  password: "secure_password"
  database: "echocloud_db"
```

---

## Serverstruktur

```
servers/
├── ServerType1/
│   ├── Server-1/
│   │   ├── run.sh
│   │   ├── server.properties
│   │   └── server.jar
│   └── Server-2/
└── ServerType2/
    └── Server-3/
```

Jeder Serverordner muss enthalten:

* `run.sh`: Startskript mit Screen-Konfiguration
* `server.properties`: Minecraft-Server-Konfiguration
* Server-JAR-Datei

---

## Sicherheitsfeatures

* **Token-basierte Authentifizierung**: Jeder Server erhält eindeutige Zugangstokens
* **HTTPS/WSS**: Alle Verbindungen verschlüsselt
* **Automatisch generierte Zertifikate**: Für Entwicklungszwecke
* **CORS-Schutz**: Konfigurierbar
* **Eingabevalidierung**: Alle Anfragen werden geprüft

---

## Entwicklung

### Eigene Befehle hinzufügen

```python
def cmd_custom(self, args):
    """Implementierung eines eigenen Befehls"""
    pass

self.register_command("custom", self.cmd_custom)
self.add_help_message("custom", "Beschreibung des Kommandos")
```

### Datenbankoperationen

```python
# Daten speichern
storage_manager.store_data("key", {"data": "value"})

# Daten abrufen
data = storage_manager.get_data("key")

# Daten löschen
storage_manager.delete_data("key")
```

---

## Mitwirken

1. Fork des Repositories
2. Feature-Branch erstellen (`git checkout -b feature/neues-feature`)
3. Änderungen committen (`git commit -am 'Neues Feature'`)
4. Branch pushen (`git push origin feature/neues-feature`)
5. Pull Request erstellen

---

## Support

Für Support bitte ein Issue auf GitHub öffnen oder das Entwicklerteam kontaktieren.

---

**EchoCloud** – Professionelles Minecraft-Servermanagement einfach gemacht.

---

