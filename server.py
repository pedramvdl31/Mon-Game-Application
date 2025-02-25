from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import logging
import json  # Ensure json is imported
from models import User  # Import your User model
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
import time

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Get the directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files from the root directory
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

# Get URLs from environment variables, defaulting to localhost if not set
API_URL = os.getenv("API_URL")

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in .env!")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# Store active games (only one active game at a time for now)
active_game: Optional[Dict] = None

@app.get("/config")
def get_config():
    return {"api_url": API_URL}

@app.get("/")
def serve_index():
    return FileResponse("index.html")

class UserCreate(BaseModel):
    name: str

class GameModeSelect(BaseModel):
    name: str
    game_mode: str

class UserDisconnect(BaseModel):
    name: str

@app.post("/create-user")
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        logging.debug(f"Received request to create user: {user.name}")

        existing_user = db.query(User).filter(User.unique_id == user.name).first()
        if existing_user:
            db.close()
            return {"message": "User already exists"}

        new_user = User(unique_id=user.name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logging.info(f"User {user.name} created successfully")
        return {"message": "User created successfully"}
    
    except Exception as e:
        logging.error(f"Error occurred while creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()

@app.post("/select-game-mode")
async def select_game_mode(selection: GameModeSelect):
    global active_game
    if active_game:
        if active_game["game"] == selection.game_mode and active_game["players"]["player2"] is None:
            active_game["players"]["player2"] = selection.name
            active_game["game_status"] = "started"
            return {"message": "Game started", "game": selection.game_mode}
    else:
        active_game = {
            "game": selection.game_mode,
            "game_status": "waiting",
            "players": {"player1": selection.name, "player2": None}
        }
    return {"message": "Game mode selected", "game": selection.game_mode}

@app.post("/disconnect-user")
async def disconnect_user(request: Request):
    global active_game
    body = await request.body()
    data = json.loads(body.decode("utf-8"))
    name = data.get("name")

    if not name or not isinstance(name, str):
        raise HTTPException(status_code=400, detail="Invalid name format")

    db = SessionLocal()
    db.query(User).filter(User.unique_id == name).delete()
    db.commit()
    db.close()

    if active_game and name in active_game["players"].values():
        active_game = None

    return {"message": "User disconnected"}

@app.get("/game-status")
def game_status():
    total_players = sum(1 for player in active_game["players"].values() if player is not None) if active_game else 0
    return {"game": active_game, "total_players": total_players}

@app.get("/player-vs-ai-game-status")
async def player_vs_ai_status():
    # Provide the current state of the Player vs AI game.
    # Include board position information if needed.
    return 0

@app.get("/ai-vs-ai-game-status")
async def ai_vs_ai_status():
    # Provide the current state of the AI vs AI game.
    # Include board position information if needed.

    return 0
