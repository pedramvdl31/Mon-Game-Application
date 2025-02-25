from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
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

# Get URLs from environment variables, defaulting to localhost if not set
API_URL = os.getenv("API_URL")

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in .env!")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# Store active games (temporary storage for demo purposes)
active_games: Dict[str, Dict] = {}

@app.get("/config")
def get_config():
    return {"api_url": API_URL}

@app.get("/")
def serve_index():
    return FileResponse("index.html")

class UserCreate(BaseModel):
    name: str  # Updated from unique_id to name to match AJAX request

@app.post("/create-user")
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        logging.debug(f"Received request to create user: {user.name}")

        existing_user = db.query(User).filter(User.unique_id == user.name).first()
        if existing_user:
            db.close()
            return {"message": "User already exists"}

        new_user = User(unique_id=user.name)  # Storing name as unique_id
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

class GameStatusResponse(BaseModel):
    game: str
    game_status: str
    players: Dict[str, Optional[str]]

@app.get("/game-status")
def game_status():
    # Simulated game state (replace with database query or actual logic)
    return GameStatusResponse(
        game="pvsp",  # Example game type
        game_status="waiting",  # Example status
        players={"player1": "name1", "player2": "name2"}  # Example players
    )
