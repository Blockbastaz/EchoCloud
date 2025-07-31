from fastapi import APIRouter
from core.server_manager import ServerManager

router = APIRouter()
servermanager = ServerManager()

# Nur Beispielsweise Hinzugefügt.

@router.post("/start/{server_name}")
async def start(server_name: str):
    return servermanager.start_server(server_name)

@router.post("/stop/{server_name}")
async def stop(server_name: str):
    return servermanager.stop_server(server_name)
