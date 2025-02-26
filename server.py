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
from ai_logic import ai_make_move, check_win

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Serve static files from the root directory
app.mount("/static", StaticFiles(directory="static"), name="static")

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
            "players": {"player1": selection.name, "player2": None},
            "board": [['_' for _ in range(7)] for _ in range(7)]  # ✅ Initialize the board
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
    global active_game
    
    if not active_game:
        return {
            "game": {
                "game_status": "waiting",
                "players": {"player1": None, "player2": None},
                "board": [['_' for _ in range(7)] for _ in range(7)],
                "current_turn": None,
                "game_over": False  # ✅ Default: game not over
            },
            "total_players": 0
        }

    if "board" not in active_game or active_game["board"] is None:
        active_game["board"] = [['_' for _ in range(7)] for _ in range(7)]  # Ensure board exists

    if "current_turn" not in active_game:
        active_game["current_turn"] = active_game["players"]["player1"]  # Default to Player 1

    if "game_over" not in active_game:
        active_game["game_over"] = False  # Ensure game_over exists at the correct level

    total_players = sum(1 for player in active_game["players"].values() if player is not None)

    return {
        "game": active_game,  # ✅ This now includes `game_over` correctly
        "total_players": total_players
    }

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

class UpdateGame(BaseModel):
    player: str  # The player making the move
    board: List[List[str]]  # The updated board
    game_over: bool  # New: Game over status

@app.post("/update-game")
async def update_game(update: UpdateGame):
    global active_game

    if not active_game:
        raise HTTPException(status_code=400, detail="No active game.")

    if update.player not in active_game["players"].values():
        raise HTTPException(status_code=403, detail="Player not part of the game.")

    # ✅ Validate board structure
    if not isinstance(update.board, list) or len(update.board) != 7 or any(len(row) != 7 for row in update.board):
        raise HTTPException(status_code=400, detail="Invalid board format. Expected a 7x7 array.")

    # ✅ Update the game board
    active_game["board"] = update.board

    # ✅ Store `game_over` correctly (DIRECTLY inside `active_game`)
    active_game["game_over"] = update.game_over

    # ✅ Switch turn only if the game is not over
    if not update.game_over:
        if update.player == active_game["players"]["player1"]:
            active_game["current_turn"] = active_game["players"]["player2"]  # Switch to Player 2
        else:
            active_game["current_turn"] = active_game["players"]["player1"]  # Switch to Player 1

    return {
        "message": "Game updated successfully",
        "board": active_game["board"],
        "current_turn": active_game["current_turn"]
    }
    
class GameBoard(BaseModel):
    board: List[List[str]]
    ai_symbol: str  # 'x' or 'o'

@app.post("/ai-move")
async def get_ai_move(game_board: GameBoard):
    board = game_board.board
    ai_symbol = game_board.ai_symbol  # Get the AI's symbol ('x' or 'o')

    # Ensure the board is valid
    if not isinstance(board, list) or len(board) != 7 or any(len(row) != 7 for row in board):
        raise HTTPException(status_code=400, detail="Invalid board format. Expected a 7x7 array.")

    # AI makes a move with its assigned symbol
    updated_board = ai_make_move(board, ai_symbol)

    return {"message": "AI has moved", "board": updated_board}