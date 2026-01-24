from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from detection import detect_objects
# from summarization import create_summary
# from storage import add_event, query_events
# from utils import decode_image
from websocket import socket_router, frame_buffer, processed_buffer
from vision_worker import VisionWorker
import datetime, uvicorn, threading, asyncio
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the YOLO worker in a background thread
    worker = VisionWorker(frame_buffer, processed_buffer)
    thread = threading.Thread(target=worker.run, daemon=True)
    thread.start()
    
    print("[INFO] YOLO Worker started")
    
    yield  # Application runs here
    
    print("[INFO] Lifespan ending — cleanup if needed")
    # If you had cleanup logic, join threads or release resources here



app = FastAPI(lifespan=lifespan)

# Allow all origins, methods, headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, etc)
    allow_headers=["*"],        # Allow all headers
)

router = APIRouter()

app.include_router(router, prefix="/api")
app.include_router(socket_router, prefix="/ws")

@router.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy"})

@router.get("/tasks")
async def tasks():
    return JSONResponse(content={"tasks": [f"Task: {task.get_name()}, Done: {task.done()}"] for task in asyncio.all_tasks() })


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)