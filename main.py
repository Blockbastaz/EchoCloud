from fastapi import FastAPI
from api.endpoints import router as api_router
from utils.logger import setup_logger

app = FastAPI(title="Minecraft Cloud Controller")
app.include_router(api_router)

setup_logger()
