from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Users Table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String, unique=True, nullable=False)

    games_as_user1 = relationship("Game", foreign_keys="[Game.user_1]")
    games_as_user2 = relationship("Game", foreign_keys="[Game.user_2]")
    moves = relationship("Move", back_populates="user")

# Games Table
class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_1 = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_2 = Column(Integer, ForeignKey("users.id"), nullable=True)
    game_status = Column(String, nullable=False)  # "waiting", "in_progress", "finished"
    user_won = Column(Integer, ForeignKey("users.id"), nullable=True)  # Winner user_id if finished

    moves = relationship("Move", back_populates="game")

# Moves Table
class Move(Base):
    __tablename__ = "moves"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    row = Column(Integer, nullable=False)  # 0-6
    column = Column(Integer, nullable=False)  # 0-6
    created_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="moves")
    user = relationship("User", back_populates="moves")
