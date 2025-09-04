
---

<p align="center">
  <img src="https://github.com/Blockbastaz/EchoCloud/blob/main/data/logo.png" alt="EchoCloud Logo" width="200"/>
</p>

<h1 align="center">EchoCloud</h1>

<p align="center">
  <strong>Das modulare Command-Line- & API-Tool für Minecraft-Server-Management</strong><br/>
  <em>Effizient. Sicher. Erweiterbar.</em>
</p>

---

## 🌐 Überblick

**EchoCloud** ist ein modernes Python-CLI-System für die Verwaltung mehrerer Minecraft-Server, das **sowohl lokal als auch über HTTPS erreichbar** ist. Es kombiniert **flexibles Servermanagement**, **erweiterbare APIs** und **persistente Speicherung** in einer klar strukturierten Architektur.

Die Software ist modular aufgebaut, sodass du nur die Komponenten nutzt, die du brauchst: **CLI, APIManager, ServerManager, CommandManager und Storage**.

---

## ✨ Key Features

| Feature                 | Beschreibung                                                                                                                                                      |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Modulares CLI**       | Rich-basierte, interaktive Kommandozeile mit Farbausgabe und strukturierter Übersicht für Server, Logs und Aktionen.                                              |
| **APIManager**          | HTTPS-fähige API für externe Plugins oder Tools. Authentifizierung via Tokens pro Server. Vollständig WebSocket-kompatibel für **Server → Client Kommunikation**. |
| **ServerManager**       | Verwaltung von beliebig vielen Serverinstanzen gleichzeitig. Start, Stop, Statusabfrage, Logs – alles aus einer Konsole.                                          |
| **CommandManager**      | Erweiterbares Befehlsframework für server-spezifische Aktionen, das beliebig ergänzt werden kann.                                                                 |
| **Storage**             | Persistente Speicherung von Konfigurationen, Logs und benutzerdefinierten Daten. Unterstützt **MySQL, MariaDB, PostgreSQL und H2**.                               |
| **HTTPS & Zertifikate** | Automatische Zertifikatsgenerierung für sichere Kommunikation mit Plugins und WebClients.                                                                         |
| **Autoregistration**    | Automatisches Registrieren neuer Server aus einem konfigurierten Standardpfad.                                                                                    |
| **Debug Mode**          | Detaillierte Entwickler-Logs für schnelle Fehlerdiagnose und Monitoring.                                                                                          |
| **Cross-Platform**      | Lauffähig auf Linux, Windows und Mac, kompatibel mit allen gängigen Minecraft-Versionen.                                                                          |

---

## 💾 Storage & Persistenz

EchoCloud kann Daten auf unterschiedliche Arten speichern, je nach Projektgröße und Anforderungen:

| Typ                 | Beschreibung                                                                           |
| ------------------- | -------------------------------------------------------------------------------------- |
| **MySQL / MariaDB** | Klassische relationale Datenbank, geeignet für mittelgroße bis große Projekte.         |
| **PostgreSQL**      | Leistungsstark, ideal für umfangreiche Daten und komplexe Queries.                     |
| **H2**              | Leichte, dateibasierte Java-Datenbank – perfekt für kleine Projekte oder lokale Tests. |

**Konfiguration:**

```yaml
storage:
  storage_type: "h2"           # h2, mysql, mariadb, postgresql
  host: "localhost"
  port: 3306
  username: "root"
  password: "passwort"
  database: "EchoCloud"
  table_name: "json_storage"
  h2_file_path: "../data/"
```

---

## 🔒 Sicherheit & Authentifizierung

* Jeder Server erhält einen **eigenen Auth-Token**, gespeichert in `auth_tokens.yaml`.
* HTTPS wird standardmäßig unterstützt; Zertifikate können automatisch generiert werden (`cert.pem` & `key.pem`).
* WebSocket-Kommunikation erlaubt bidirektionale Nachrichten: **Server → Client** oder **Client → Server**.

---

## 🚀 Installation

### 1️⃣ Vorbereitung

```bash
cd EchoCloud/EchoCloud
sudo chmod +x install.sh
```

> `sudo` stellt sicher, dass das Skript ausführbar ist.

---

### 2️⃣ Installation starten

```bash
./install.sh
```

* Installiert Abhängigkeiten
* Erstellt Standardkonfigurationen
* Generiert initiale Serverliste

---

### 3️⃣ Bestehende Server importieren

* Passe `default_path` in `settings.yaml` an:

```yaml
default_path: "../Cloud/running/static"
```

* EchoCloud scannt diesen Ordner automatisch und erstellt Konfigurationsdateien für alle vorhandenen Server.

---

### 4️⃣ Server auswählen & starten

```text
select Proxy-1
start
```

* Server läuft im Hintergrund via `screen`.
* Logs können live über die CLI angezeigt werden.

---

### 5️⃣ CLI & Commands

| Befehl                    | Beschreibung                                                       |
| ------------------------- | ------------------------------------------------------------------ |
| `status`                  | Zeigt Status, CPU, RAM und Online-Status des ausgewählten Servers. |
| `servers`                 | Listet alle bekannten Server auf.                                  |
| `select <server>`         | Wählt einen Server für Befehle aus.                                |
| `config [option] [value]` | Zeigt oder ändert Konfigurationen.                                 |
| `start`                   | Startet den ausgewählten Server im Hintergrund.                    |
| `stop`                    | Stoppt den Server sauber.                                          |
| `logs`                    | Zeigt die aktuellen Logs in Echtzeit.                              |
| `help`                    | Zeigt alle verfügbaren Befehle.                                    |
| `autoscan`                | Scannt `default_path` nach neuen Servern.                          |
| `debug`                   | Aktiviert Entwickler-Logs für detailliertes Monitoring.            |
| `reload`                  | Lädt Serverkonfiguration neu, ohne den Server zu stoppen.          |

💡 **Tipp:** Immer zuerst `select <server>` ausführen, bevor `start` oder `stop` verwendet wird.

---

## 🌍 API & WebSocket

* **POST Endpoint für Plugins:** `/api/plugin/{server_id}/{auth_token}`
  JSON-Beispiel:

  ```json
  {
    "playerName": "Steve",
    "action": "jump"
  }
  ```
* **WebSocket Endpoint:** `/ws/{server_id}/{auth_token}`

  * Echtzeit-Kommunikation Server → Plugin
  * Authentifizierung via Token
  * Ideal für Events, Benachrichtigungen oder Remote-Control

---

## ⚙️ Konfiguration (settings.yaml)

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
```

---

## 📝 Modernes, flexibles Design

* **Modular**: CLI, API, Storage, Server- & CommandManager unabhängig.
* **Sicher**: Auth, HTTPS, selbstsignierte Zertifikate oder CA.
* **Erweiterbar**: Eigene Commands, neue Storage-Typen, Plugins.
* **Cross-Platform**: Linux, Windows, MacOS.

---

