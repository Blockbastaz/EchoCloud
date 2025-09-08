import secrets
import threading
import asyncio
import json
from time import struct_time
from typing import Dict
from pathlib import Path
from datetime import datetime

import uvicorn
import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.console import pInfo, pWarning, pDebug, pError
from core.server_manager import ServerManager, ServerState
from utils.certgen import generate_self_signed_cert
from fastapi import Request
import redis.asyncio as aioredis

from utils.storagemanager import StorageManager

class APIManager:
    def __init__(self,
                 server_manager: ServerManager,
                 storage_manager: StorageManager,
                 host: str = "0.0.0.0",
                 port: int = 8080,
                 auth_config_path: str = "./config/auth_tokens.yaml",
                 cert_file_path: Path = "./config/cert.pem",
                 key_file_path: Path = "./config/key.pem",
                 cert_duration_days: int = 365,
                 heartbeat_delay: int = 10,
                 autocert: bool = True,
                 use_https: bool = True,
                 communication_type: str = "websocket",
                 redis_channel: str = "echocloud:all",
                 redis_password: str = "passwort",
                 redis_user: str = "default"):
        self.cert_file_path: Path = cert_file_path
        self.key_file_path: Path = key_file_path
        self.autocert: bool = autocert
        self.use_https: bool = use_https
        self.server_manager: ServerManager = server_manager
        self.host: str = host
        self.port: int = port
        self.cert_duration_days = cert_duration_days
        self.clients: Dict[str, WebSocket] = {}
        self.thread = None
        self.server = None
        self.heartbeat_delay: int = heartbeat_delay
        self.heartbeat_task = None
        self.heartbeat_running: bool = False
        self.storage_manager: StorageManager = storage_manager
        self.communication_type: str = communication_type.lower()
        self.redis = None
        self.redis_pubsub = None
        self.redis_task = None
        self.redis_channel: str = redis_channel
        self.redis_password: str = redis_password
        self.redis_user: str = redis_user
        self.should_stop: bool = False  # ADD THIS: Shutdown flag

        self.auth_tokens: Dict[str, str] = self.load_auth_tokens(auth_config_path)

        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.setup_routes()
        if use_https:
            self.setup_https()

    def setup_https(self):
        if not self.communication_type == "redis":
            if self.cert_file_path.exists() and self.key_file_path.exists():
                pInfo("HTTPS Zertifikat Importiert ✓")
            else:
                if self.autocert:
                    generate_self_signed_cert(cert_path=self.cert_file_path, key_path=self.key_file_path, host=self.host,
                                      cert_duration_days=self.cert_duration_days)
                    pInfo("HTTPS Zertifikat Erstellt ✓")
                else:
                    pError("HTTPS Zertifikat nicht gefunden. Autocert ist Deaktiviert, weshalb es nicht automatisch erstellt wird. Aktiviere Autocert in config/settings.yaml")

    async def init_redis(self):
        """Initialisiert Redis Verbindung wenn communication_type=redis"""
        if self.redis is None:
            self.redis = aioredis.from_url(f"redis://{self.host}:{self.port}", password=self.redis_password,decode_responses=True)
            self.redis_pubsub = self.redis.pubsub()

            await self.redis_pubsub.subscribe("echocloud:all")

            async def reader():
                try:
                    async for message in self.redis_pubsub.listen():
                        if self.should_stop:
                            break
                        if message["type"] == "message":
                            try:
                                data = json.loads(message["data"])
                                server_id = data.get("server_id")
                                msg_type = data.get("type")
                                if msg_type == "heartbeat_response":
                                    self.process_heartbeat_response(server_id, data)
                                else:
                                    pInfo(f"[Redis Daten] {server_id}: {data}")
                            except Exception as e:
                                if not self.should_stop:
                                    pWarning(f"Redis Nachricht Fehler: {e}")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    if not self.should_stop:
                        pWarning(f"Redis Reader Fehler: {e}")

            self.redis_task = asyncio.create_task(reader())
            self.start_heartbeat()
            pInfo("Redis Kommunikation gestartet ✓")

    def load_auth_tokens(self, path: str) -> Dict[str, str]:
        tokens = {}

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            with open(path, "r") as f:
                tokens = yaml.safe_load(f) or {}

        updated = False

        for srv in self.server_manager.servers:
            if srv.server_id not in tokens:
                tokens[srv.server_id] = secrets.token_hex(32)
                pInfo(f"Neuer Token generiert für '{srv.server_id}'")
                updated = True

        if not path.exists() or updated:
            with open(path, "w") as f:
                yaml.dump(tokens, f)
            pInfo(f"Auth-Datei aktualisiert: '{path}'")

        return tokens

    async def heartbeat_loop(self):
        """Sendet regelmäßig Heartbeats"""
        while self.heartbeat_running and not self.should_stop:
            try:
                if self.communication_type == "websocket": # Websocket
                    for server_id, websocket in list(self.clients.items()):
                        try:
                            heartbeat_request = {
                                "type": "heartbeat_request",
                                "timestamp": datetime.now().isoformat()
                            }
                            await websocket.send_text(json.dumps(heartbeat_request))
                            pDebug(f"Heartbeat-Request an {server_id} gesendet")
                        except Exception as e:
                            pWarning(f"Fehler beim Senden von Heartbeat an {server_id}: {e}")
                            self.clients.pop(server_id, None)
                            server = self.server_manager.get_server_by_id(server_id)
                            if server:
                                server.server_state = ServerState.OFFLINE
                                server.is_running = False
                                server.start_time = None
                else:  # Redis
                    if self.redis and not self.should_stop:
                        for server in self.server_manager.servers:
                            heartbeat_request = {
                                "type": "heartbeat_request",
                                "server_id": server.server_id,
                                "timestamp": datetime.now().isoformat()
                            }
                            try:
                                await self.redis.publish(f"echocloud:{server.server_id}", json.dumps(heartbeat_request))
                                pDebug(f"Heartbeat-Request an {server.server_id} über Redis gesendet")
                            except Exception as e:
                                if not self.should_stop:
                                    pWarning(f"Redis Heartbeat Fehler: {e}")
                                break

                await asyncio.sleep(self.heartbeat_delay)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self.should_stop:
                    pWarning(f"Fehler im Heartbeat-Loop: {e}")
                    await asyncio.sleep(1)

    def start_heartbeat(self):
        if not self.heartbeat_running:
            self.heartbeat_running = True
            self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
            print("\n") # Wegen Zeilen Bug. Nachricht Kommt aus anderer Thread. Wiederspricht sich mit Commandmanager.
            pInfo(f"Heartbeat-System gestartet (Intervall: {self.heartbeat_delay}s)")

    def stop_heartbeat(self):
        self.heartbeat_running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            pInfo("Heartbeat-System gestoppt")

    def process_heartbeat_response(self, server_id: str, data: dict):
        server = self.server_manager.get_server_by_id(server_id)
        if not server:
            pWarning(f"Unbekannter Server: {server_id}")
            return

        try:
            state_str = data.get("server_state")
            if state_str and state_str in [s.value for s in ServerState]:
                server.server_state = ServerState(state_str)
                server.is_running = server.server_state == ServerState.ONLINE
            else:
                server.is_running = data.get("is_running", False)
                server.server_state = ServerState.ONLINE if server.is_running else ServerState.OFFLINE

            if server.is_running and not server.start_time:
                start_time_str = data.get("start_time")
                if start_time_str:
                    try:
                        server.start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    except:
                        server.start_time = datetime.now()
                else:
                    server.start_time = datetime.now()
            elif not server.is_running:
                server.start_time = None

            tps = data.get("tps")
            cpu_usage = data.get("cpu_usage")
            ram_usage = data.get("ram_usage_mb")

            if tps is not None and cpu_usage is not None and ram_usage is not None:
                server.update_metrics(
                    tps=float(tps),
                    cpu_usage=float(cpu_usage),
                    ram_usage=float(ram_usage)
                )

            players_online = data.get("players_online", [])
            max_players = data.get("max_players", 0)
            server.update_players(players_online, max_players)

            pDebug(f"Heartbeat von {server_id}: Status={server.server_state.value}, "
                   f"TPS={server.tps}, CPU={server.cpu_usage}%, RAM={server.ram_usage_mb}MB, "
                   f"Spieler={len(server.players_online)}/{server.max_players}")

        except Exception as e:
            pWarning(f"Fehler beim Verarbeiten von Heartbeat-Daten von {server_id}: {e}")

    def setup_routes(self):
        @self.app.websocket("/ws/{server_id}/{auth_token}")
        async def websocket_endpoint(websocket: WebSocket, server_id: str, auth_token: str):
            expected_token = self.auth_tokens.get(server_id)
            if not expected_token or not secrets.compare_digest(expected_token, auth_token):
                await websocket.close(code=1008)
                pWarning(f"Auth fehlgeschlagen für {server_id}.")
                return

            await websocket.accept()
            self.clients[server_id] = websocket
            pInfo(f"Server verbunden: {server_id}")

            if not self.heartbeat_running:
                self.start_heartbeat()

            try:
                while True:
                    data = await websocket.receive_text()
                    try:
                        json_data = json.loads(data)
                        message_type = json_data.get("type")

                        if message_type == "heartbeat_response":
                            self.process_heartbeat_response(server_id, json_data)
                        else:
                            pInfo(f"[Daten] {server_id}: {data}")
                    except json.JSONDecodeError:
                        pInfo(f"[Daten] {server_id}: {data}")

            except WebSocketDisconnect:
                self.clients.pop(server_id, None)
                pWarning(f"Verbindung getrennt: {server_id}")

                server = self.server_manager.get_server_by_id(server_id)
                if server:
                    if server.server_state != ServerState.STOPPING:
                        server.server_state = ServerState.CRASHED
                        pWarning(f"Server {server_id} unerwartet abgestürzt")
                    else:
                        server.server_state = ServerState.OFFLINE
                    server.is_running = False
                    server.start_time = None

        @self.app.get("/api/ping")
        async def ping():
            return JSONResponse({"status": "ok"})

        @self.app.get("/api/servers")
        async def get_servers():
            servers_data = []
            for server in self.server_manager.servers:
                server_info = {
                    "server_id": server.server_id,
                    "name": server.name,
                    "ip": server.ip,
                    "port": server.port,
                    "server_type": server.server_type,
                    "software": server.software.value,
                    "software_version": server.software_version,
                    "server_state": server.server_state.value,
                    "is_running": server.is_running,
                    "start_time": server.start_time.isoformat() if server.start_time else None,
                    "tps": server.tps,
                    "cpu_usage": server.cpu_usage,
                    "ram_usage_mb": server.ram_usage_mb,
                    "players_online": server.players_online,
                    "max_players": server.max_players,
                    "uptime": server.get_uptime(),
                    "java_memory": server.java_memory,
                    "connected": server.server_id in self.clients
                }
                servers_data.append(server_info)

            return JSONResponse({"servers": servers_data})

        @self.app.get("/api/server/{server_id}")
        async def get_server(server_id: str):
            server = self.server_manager.get_server_by_id(server_id)
            if not server:
                raise HTTPException(status_code=404, detail="Server nicht gefunden")

            server_info = {
                "server_id": server.server_id,
                "name": server.name,
                "ip": server.ip,
                "port": server.port,
                "server_type": server.server_type,
                "software": server.software.value,
                "software_version": server.software_version,
                "server_state": server.server_state.value,
                "is_running": server.is_running,
                "start_time": server.start_time.isoformat() if server.start_time else None,
                "tps": server.tps,
                "cpu_usage": server.cpu_usage,
                "ram_usage_mb": server.ram_usage_mb,
                "players_online": server.players_online,
                "max_players": server.max_players,
                "plugins": server.plugins,
                "uptime": server.get_uptime(),
                "java_memory": server.java_memory,
                "connected": server.server_id in self.clients,
                "last_output_lines": server.last_output_lines
            }

            return JSONResponse(server_info)

        @self.app.post("/api/plugin/{server_id}/{auth_token}")
        async def plugin_endpoint(server_id: str, auth_token: str, request: Request):
            expected_token = self.auth_tokens.get(server_id)
            if not expected_token or not secrets.compare_digest(expected_token, auth_token):
                raise HTTPException(status_code=401, detail="Auth fehlgeschlagen")

            data = await request.json()  # JSON-Daten vom Plugin
            player_name = data.get("playerName")
            player_uuid = data.get("uuid")
            action = data.get("action")

            pInfo(f"Plugin Daten von {server_id} - Spieler: {player_name}({player_uuid}), Aktion: {action}")

            if server_id in self.clients:
                await self.send_message(server_id, f"Aktion empfangen: {action} von {player_name}")

            return JSONResponse({"status": "success", "received": data})

        @self.app.post("/api/logs/{server_id}/{auth_token}")
        async def log_endpoint(server_id: str, auth_token: str, request: Request):
            expected_token = self.auth_tokens.get(server_id)
            if not expected_token or not secrets.compare_digest(expected_token, auth_token):
                raise HTTPException(status_code=401, detail="Auth fehlgeschlagen")

            data = await request.json()
            player_name = data.get("playerName")
            player_uuid = data.get("uuid")
            action = data.get("action")
            forced = data.get("forced", False)
            now = datetime.now()

            if not player_name or action not in ("join", "leave"):
                raise HTTPException(status_code=400, detail="Ungültige Log-Daten")

            logs_key = f"logs:{server_id}:{player_name}:{player_uuid}"
            logs = self.storage_manager.get_data(logs_key) or {
                "player": player_name,
                "uuid": player_uuid,
                "server_id": server_id,
                "sessions": [],
                "total_playtime_seconds": 0,
                "last_join": None
            }

            if action == "join":
                logs["last_join"] = now.isoformat()
                pInfo(f"[Logs] Spieler {player_name} ist dem Server {server_id} beigetreten")

            elif action == "leave":
                join_time = logs.get("last_join")
                if join_time:
                    try:
                        join_dt = datetime.fromisoformat(join_time)
                        session_seconds = int((now - join_dt).total_seconds())
                        logs["total_playtime_seconds"] += session_seconds
                        logs["sessions"].append({
                            "join": join_dt.isoformat(),
                            "leave": now.isoformat(),
                            "forced": forced,
                            "duration_seconds": session_seconds
                        })
                    except Exception as e:
                        pWarning(f"Konnte Session-Dauer nicht berechnen für {player_name}: {e}")
                logs["last_join"] = None
                pInfo(f"[Logs] Spieler {player_name} hat den Server {server_id} verlassen (forced={forced})")

            self.storage_manager.store_data(logs_key, logs)

            return JSONResponse({"status": "success", "logs": logs})

    async def send_message(self, server_id: str, message: str):
        if self.communication_type == "websocket":
            websocket = self.clients.get(server_id)
            if websocket:
                await websocket.send_text(message)
            else:
                raise HTTPException(status_code=404, detail=f"Client '{server_id}' nicht verbunden.")
        else:  # Redis
            if not self.redis:
                await self.init_redis()
            payload = json.dumps({
                "server_id": server_id,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            await self.redis.publish(f"echocloud:{server_id}", payload)

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def cleanup_and_exit():
            if self.redis_task:
                self.redis_task.cancel()
                try:
                    await self.redis_task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    pWarning(f"Fehler beim Beenden des Redis Tasks: {e}")

            if self.redis_pubsub:
                try:
                    await self.redis_pubsub.unsubscribe()
                    await self.redis_pubsub.close()
                except Exception as e:
                    pWarning(f"Fehler beim Schließen von Redis PubSub: {e}")

            if self.redis:
                try:
                    await self.redis.close()
                except Exception as e:
                    pWarning(f"Fehler beim Schließen von Redis: {e}")

        try:
            if self.communication_type == "redis":
                loop.run_until_complete(self.init_redis())

                async def wait_for_stop():
                    while not self.should_stop:
                        await asyncio.sleep(0.1)

                loop.run_until_complete(wait_for_stop())
                loop.run_until_complete(cleanup_and_exit())
            else:
                config = uvicorn.Config(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="info",
                    ssl_certfile=self.cert_file_path if self.use_https else None,
                    ssl_keyfile=self.key_file_path if self.use_https else None
                )
                self.server = uvicorn.Server(config)
                loop.run_until_complete(self.server.serve())
                pInfo("Cloud Manager API [green]Online[/green] ✓")
        except Exception as e:
            pError(f"Fehler im API Manager Loop: {e}")
        finally:
            if self.communication_type == "redis":
                try:
                    loop.run_until_complete(cleanup_and_exit())
                except Exception as e:
                    pWarning(f"Fehler beim Cleanup: {e}")
            loop.close()

    def start_in_thread(self):
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop_thread(self):
        pInfo("Cloud Manager API [red]Offline[/red] ✓")
        self.stop_heartbeat()

        self.should_stop = True

        if self.communication_type != "redis":
            if hasattr(self, "server") and self.server:
                self.server.should_exit = True

        # Wait for thread to finish with timeout
        if hasattr(self, "thread") and self.thread:
            self.thread.join(timeout=5.0)
            if self.thread.is_alive():
                pWarning("Thread did not stop within timeout, but continuing shutdown...")

        self.redis = None
        self.redis_pubsub = None
        self.redis_task = None