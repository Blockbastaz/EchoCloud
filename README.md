
<p align="center">
  <img src="https://github.com/Blockbastaz/EchoCloud/blob/main/data/logo.png" alt="EchoCloud Logo" width="200"/>
</p>

<h1 align="center">EchoCloud</h1>

<p align="center">
  <strong>Modulares Server-Management-System für Minecraft-Infrastrukturen</strong><br/>
  <em>Effizient • Sicher • Erweiterbar</em>
</p>

---

## 📖 Übersicht

**EchoCloud** ist ein Python-basiertes CLI- und API-System zur zentralen Verwaltung mehrerer Minecraft-Serverinstanzen.  
Es bietet Echtzeitüberwachung, sichere Kommunikation, persistente Speicherung und eine modulare Architektur.

---

## ⚡ Hauptfunktionen

- 🖥️ **Multi-Server-Verwaltung** – Zentrale Kontrolle über alle Serverinstanzen
- 🌐 **REST-API & WebSockets** – Echtzeit-Kommunikation zwischen Servern und Cloud
- 💾 **Persistente Speicherung** – Unterstützt MySQL, MariaDB, PostgreSQL & H2
- 🧠 **Auto-Discovery** – Automatische Erkennung & Registrierung neuer Server
- 🖲️ **Serversteuerung per CLI** – Starten, Stoppen & Befehle senden direkt aus der EchoCloud CLI
- 🧩 **Tab Completion** – Intelligente Autovervollständigung für CLI-Kommandos
- ⚡ **Crash Detection** – Automatische Erkennung und Meldung nicht mehr antwortender Server
- 🧮 **Server-Logs in Echtzeit** – Aktuell verfügbar: Join/Leave-Events aller Spieler im Netzwerk
- 🔐 **Sichere Kommunikation** – HTTPS/WSS mit automatischer Zertifikatserstellung
- 🖥️ **Screen-Integration** – Nahtlose Verwaltung von Linux-Screen-Sessions

---

## 🧩 Architektur

```

EchoCloud/
├── core/
│   ├── server\_manager.py
│   ├── console.py
│   └── certgen.py
├── commands/
│   └── commandmanager.py
├── api/
│   └── apimanager.py
├── utils/
│   └── storagemanager.py
└── config/
└── settings.yaml

````

---

## ⚙️ Voraussetzungen

- **Python 3.8+**
- **Linux/Unix**
- **Java**

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/EchoCloud.git
cd EchoCloud
chmod +x install.sh
./install.sh
````

Automatische Server-Erkennung starten:

```bash
autoscan
```

> Das Skript installiert alle Abhängigkeiten und legt die Standardverzeichnisse für Server und Datenbanken an.

---

## ⚙️ Konfiguration

Bearbeite `config/settings.yaml`:

```yaml
server:
  default_path: "../Cloud/running/static"
  version: "paper-1.21.1-133.jar"
  check_delay: 10

cloud:
  autoregister: true
  debug_mode: false
  host: "localhost"
  port: 9989

network:
  use_https: true
  auto_cert: true
  auto_api: false
  cert_duration_days: 365
  auth_config_path: "./config/auth_tokens.yaml"
  cert_file_path: "./config/cert.pem"
  key_file_path: "./config/key.pem"

storage:
  storage_type: "h2"
  host: "localhost"
  port: 3306
  username: "root"
  password: "passwort"
  database: "EchoCloud"
  table_name: "json_storage"
  h2_file_path: "data/"
```

---

## 💻 Nutzung

### CLI starten

```bash
./run.sh
```

### Wichtige Kommandos

| Befehl           | Beschreibung                         |
| ---------------- | ------------------------------------ |
| `servers`        | Liste aller registrierten Server     |
| `select <name>`  | Server für Operationen auswählen     |
| `start` / `stop` | Ausgewählten Server starten/stoppen  |
| `status`         | Statusinformationen anzeigen         |
| `logs`           | Echtzeit-Logs (z.B. Join/Leave)      |
| `autoscan`       | Neue Server automatisch registrieren |
| `startapi`       | API-Webserver starten                |
| `debug`          | Debug-Modus ein-/ausschalten         |
| `help` / `exit`  | Hilfe anzeigen / EchoCloud beenden   |

> 💡 **Neu:** CLI bietet Tab Completion für alle Kommandos!

---

## 📡 API & WebSocket

### Authentifizierung

Tokens werden für jeden Server in `config/auth_tokens.yaml` gespeichert.

**REST API Beispiel**

```http
POST /api/plugin/{server_id}/{auth_token}
Content-Type: application/json

{
  "playerName": "Steve",
  "action": "jump",
  "data": {}
}
```

**WebSocket Beispiel**

```javascript
const ws = new WebSocket('wss://localhost:9989/ws/server_id/auth_token');

ws.send(JSON.stringify({
  "type": "command",
  "data": "say Hallo Welt"
}));
```

**Health Check**

```http
GET /api/ping
```

---

## 💾 Datenbankoptionen

| Typ          | Verwendung                     |
| ------------ |--------------------------------|
| `h2`         | Standard (lokale Datei)        |
| `mysql`      | Produktion (Lightweigt)        |
| `mariadb`    | Produktion (MySQL-kompatibel)  |
| `postgresql` | Skalierbar für große Netzwerke |

---

## ⚡ Quicklinks: Server-Integration

* 📦 [Paper-Integration (Plugin)](https://github.com/Blockbastaz/EchoCloud-Paper)
* ⚡ [Velocity-Integration (Plugin)](https://github.com/Blockbastaz/EchoCloud-Velocity)

---

## 🛡️ Sicherheit

* Token-basierte Authentifizierung
* HTTPS/WSS-Verschlüsselung
* Automatische Zertifikatserstellung
* CORS-Schutz
* Eingabevalidierung aller Requests

---

## ⚙️ Entwicklung

### Eigene Befehle registrieren

```python
def cmd_custom(self, args):
    # Eigener CLI-Befehl
    pass

self.register_command("custom", self.cmd_custom)
self.add_help_message("custom", "Beschreibung des Kommandos")
```

### Datenbankoperationen

```python
storage_manager.store_data("key", {"data": "value"})
data = storage_manager.get_data("key")
storage_manager.delete_data("key")
```

---

## ⚠️Häufige Fehler

```
[*] Fehler im API Manager Loop: Error 111 connecting to 127.0.0.1:6379. Connect call failed ('127.0.0.1', 6379).
```
Du hast Redis nicht auf deinem System installiert oder benutzt einen falschen Port/IP.
So Installierst du Redis auf einem Debian-basierten System:

```bash
sudo apt install -y redis
```
---
```
[*] Fehler im API Manager Loop: AUTH <password> called without any password configured for the default user. Are you sure your configuration is correct?
```
Du hast kein Passwort in /etc/redis/redis.conf gesetzt. Editiere es mit:
```bash
sudo nano /etc/redis/redis.conf
```
Füge eine Zeile mit `requirepass DEIN_PASSWORT` hinzu und starte Redis neu:
```bash
sudo systemctl restart redis-server
```


---

## 🤝 Mitwirken

1. Fork erstellen
2. Feature-Branch erstellen: `git checkout -b feature/neues-feature`
3. Committen: `git commit -am 'Neues Feature'`
4. Pushen: `git push origin feature/neues-feature`
5. Pull Request erstellen

---

## 📞 Support

Eröffne ein Issue auf GitHub oder kontaktiere das Entwicklerteam.

---


