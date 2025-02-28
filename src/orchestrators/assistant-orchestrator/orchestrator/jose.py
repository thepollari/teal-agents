from fastapi import FastAPI
from routes import apis, websockets, deps


# Instance of FastAPI app
app = FastAPI()

# Initialize the app components
deps.initialize()
# API router to handle standard API routes
app.include_router(apis.router)
# WebSocket router for handling WebSocket connections
app.include_router(websockets.router)
