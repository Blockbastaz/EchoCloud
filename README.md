<p align="center">
  <img src="https://github.com/Blockbastaz/EchoCloud/blob/main/data/logo.png" alt="EchoCloud Logo" width="200"/>
</p>

<h1 align="center">EchoCloud</h1>

<p align="center">
  <strong>Ein modulares Command-Line-Tool zur Verwaltung und Interaktion mit Minecraft-Servern.</strong><br/>
  <em>⚠️ Aktueller Entwicklungsstatus: Frühphase – noch nicht einsatzbereit!</em>
</p>

---

## 🧠 Überblick

**EchoCloud** ist ein flexibles, auf Python basierendes CLI-System mit API-Schnittstelle zur Fernsteuerung und Verwaltung von Serverinstanzen.

Die Anwendung bietet:
- Eine interaktive Rich-Konsole
- API-Anbindung über HTTPS
- Dynamisches Server-Management
- Erweiterbares Befehls-Framework

---

## ✨ Features

- ✅ **Kommandozeileninterface (CLI)** mit farbiger Rich-Ausgabe
- ✅ **API-Modul** (`APIManager`) läuft parallel im Hintergrund
- ✅ **ServerManager** zur Verwaltung mehrerer Serverinstanzen
- ✅ **CommandManager** mit Unterstützung für Server-spezifische Befehle
- ✅ **Modularer Aufbau** mit klarer Trennung zwischen Logik und Schnittstellen
- 🚧 **Frühphase**: Viele Funktionen sind Platzhalter oder unvollständig

---

## 🛠️ Installation

### 🐧 Linux / macOS
```bash
git clone https://github.com/Blockbastaz/EchoCloud.git
cd EchoCloud/EchoCloud
chmod +x install.sh
./install.sh