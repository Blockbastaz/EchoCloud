---

<p align="center">
  <img src="https://github.com/Blockbastaz/EchoCloud/blob/main/data/logo.png" alt="EchoCloud Logo" width="200"/>
</p>

<h1 align="center">EchoCloud</h1>

<p align="center">
  <strong>Ein modulares Command-Line-Tool zur Verwaltung von Minecraft-Servern.</strong><br/>
  <em>⚠️ Frühphase – noch nicht einsatzbereit!</em>
</p>

---

## 🧠 Überblick

**EchoCloud** ist ein flexibles Python-basiertes CLI-System mit optionaler API-Schnittstelle, um Minecraft-Server effizient zu verwalten.

Features:

* Interaktive Rich-Konsole
* API-Schnittstelle über HTTPS
* Dynamisches Server-Management
* Erweiterbares Befehls-Framework

---

## ✨ Features

* ✅ Kommandozeileninterface (CLI) mit farbiger Rich-Ausgabe
* ✅ APIManager-Modul läuft parallel im Hintergrund
* ✅ ServerManager für mehrere Serverinstanzen
* ✅ CommandManager für server-spezifische Befehle
* ✅ Modularer Aufbau: klare Trennung zwischen Logik und Interface
* 🚧 Frühphase: Viele Funktionen sind noch Platzhalter

---

## 🛠️ Installation

### 1️⃣ Vorbereitung

Setze die Berechtigungen für das Installationsskript:

```bash
cd EchoCloud/EchoCloud
sudo chmod +x install.sh
```

> 🔹 `sudo` wird benötigt, damit das Skript ausführbar ist.

---

### 2️⃣ Installation starten

```bash
./install.sh
```

Das Skript richtet die Abhängigkeiten ein und erstellt die Standardkonfigurationen.

---

### 3️⃣ Bestehende Server importieren

Falls du bereits Minecraft-Server hast, passe den `default_path` in `settings.yaml` an:

```yaml
default_path: "../Cloud/running/static"
```

> 🔹 Hier liegt der Basisordner deiner Server (`Proxy-1`, `Lobby-1` etc.).

---

### 4️⃣ Server-Konfiguration erstellen

Nach dem Setzen des Pfads wirst du gefragt, ob EchoCloud die Serverkonfigurationen generieren soll.

* Bestätige mit **ja**
* EchoCloud scannt den `default_path` und erstellt Konfigurationsdateien für alle vorhandenen Server.

---

### 5️⃣ Server auswählen & starten

1. Wähle einen Server aus der Liste, z. B.:

```text
Select server: Proxy-1
```

2. Der Server startet **im Hintergrund** über `screen`.

   * Du kannst weiterhin die Konsole nutzen, während der Server läuft.
   * `run.sh` wird automatisch ausführbar gemacht, falls nötig.

---

### 6️⃣ Serververwaltung

Mit EchoCloud kannst du jetzt:

* Server starten oder stoppen
* Logs direkt in der Rich-Konsole einsehen
* Neue Server hinzufügen, indem du deren Ordner in `default_path` legst und die Konfiguration neu generierst

---

💡 **Tipp:** Für den produktiven Einsatz achte darauf, dass alle `run.sh`-Skripte Linux-kompatible Zeilenenden (`LF`) haben, sonst kann es zu Fehlern wie `Exec format error` kommen.

---
Hier ist eine **übersichtliche Erklärung aller Befehle**, die in deinem `CommandManager` registriert sind. Ich habe sie so formuliert, dass sie direkt in die README passen:

---

## 📝 Verfügbare Befehle in EchoCloud

| Befehl                    | Beschreibung                                                                                                                                                                                  |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `status`                  | Zeigt den aktuellen Status des ausgewählten Servers an (läuft er, gestoppt, CPU/Memory, etc.).                                                                                                |
| `servers`                 | Listet alle bekannten Server auf, die EchoCloud verwaltet.                                                                                                                                    |
| `select <server>`         | Wählt einen Server aus der Liste aus, um Befehle auf ihm auszuführen. Beispiel: `select Proxy-1`.                                                                                             |
| `config [option] [value]` | Zeigt oder ändert die Konfiguration des ausgewählten Servers. Ohne Parameter: aktuelle Konfiguration anzeigen. Mit Parametern: Einstellungen ändern. Beispiel: `config java_memory Xmx2048M`. |
| `start`                   | Startet den ausgewählten Server im Hintergrund (über `screen`).                                                                                                                               |
| `stop`                    | Stoppt den ausgewählten Server, indem ein Stop-Befehl an dessen Screen gesendet wird.                                                                                                         |
| `logs`                    | Zeigt die aktuellen Logs des ausgewählten Servers direkt in der CLI an.                                                                                                                       |
| `help`                    | Zeigt die Hilfe für alle verfügbaren Befehle an.                                                                                                                                              |
| `autoscan`                | Scannt den `default_path` nach neuen Servern und erstellt ggf. Konfigurationen.                                                                                                               |
| `debug`                   | Schaltet den Debug-Modus an oder aus, um detaillierte Informationen in der CLI zu erhalten.                                                                                                   |
| `reload`                  | Lädt die Konfiguration eines Servers neu, ohne den Server komplett neu zu starten.                                                                                                            |

---

💡 **Tipp:**

* Nutze `select <server>` immer zuerst, um den Server auszuwählen, bevor du `start`, `stop` oder `logs` ausführst.
* `autoscan` ist praktisch, wenn du neue Server hinzufügst oder bestehende Serverordner verschoben hast.
* `debug` kann helfen, Probleme bei Start oder Konfiguration schneller zu identifizieren.

---

