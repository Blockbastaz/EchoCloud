import secrets
import threading
from typing import Dict
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.console import pInfo, pWarning, pDebug
from core.server_manager import ServerManager
from core import autocert, use_https, cert_file_path, key_file_path
from utils.certgen import generate_self_signed_cert


class APIManager:
    def __init__(self, server_manager: ServerManager, host: str = "0.0.0.0", port: int = 8080, auth_config_path: str ="./config/auth_tokens.yaml",
                 cert_file_path: Path = "./config/cert.pem", key_file_path: Path = "./config/key.pem", cert_duration_days: int = 365):
        self.server_manager: ServerManager = server_manager
        self.host: str = host
        self.port: int = port
        self.cert_duration_days = cert_duration_days
        self.clients: Dict[str, WebSocket] = {}  # server_id -> websocket

        # Lade sichere Tokens
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
        if cert_file_path.exists() and key_file_path.exists():
            pInfo("HTTPS Zertifikat Importiert ✓")
        else:
            generate_self_signed_cert(cert_path=cert_file_path, key_path=key_file_path, host=self.host, cert_duration_days=self.cert_duration_days)
            pInfo("HTTPS Zertifikat Erstellt ✓")


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

            try:
                while True:
                    data = await websocket.receive_text()
                    pInfo(f"[Daten] {server_id}: {data}")
            except WebSocketDisconnect:
                self.clients.pop(server_id, None)
                pWarning(f"Verbindung getrennt: {server_id}")

        @self.app.get("/api/ping")
        async def ping():
            return JSONResponse({"status": "ok"})

    async def send_message(self, server_id: str, message: str):
        websocket = self.clients.get(server_id)
        if websocket:
            await websocket.send_text(message)
        else:
            raise HTTPException(status_code=404, detail=f"Client '{server_id}' nicht verbunden.")

    def start_in_thread(self):
        def run():
            if use_https:
                uvicorn.run(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="info",
                    ssl_certfile=cert_file_path,
                    ssl_keyfile=key_file_path
                )
            else:
                uvicorn.run(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="info"
                )

                # Debug Nachrichten von Server Kommen Noch!

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        pInfo("Cloud Manager API [green]Online[/green] ✓")
