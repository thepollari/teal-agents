from fastapi import FastAPI
from routes import apis, websockets, deps
config = get_config()
from .deps import get_config


# Instance of FastAPI app
app = FastAPI()

# Initialize the app components
deps.initialize()
# API router to handle standard API routes
app.include_router(apis.router, prefix=f"/{config.service_name}/{str(config.version)}")
# WebSocket router for handling WebSocket connections
app.include_router(websockets.router, prefix=f"/{config.service_name}/{str(config.version)}")
