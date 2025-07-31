from fastapi import APIRouter
from core.server_manager import start_server, stop_server

router = APIRouter()

@router.post("/start/{server_name}")
async def start(server_name: str):
    return start_server(server_name)

@router.post("/stop/{server_name}")
async def stop(server_name: str):
    return stop_server(server_name)
