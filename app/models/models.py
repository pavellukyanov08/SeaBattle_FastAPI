import enum
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, func, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base


class Player(Base):
    __tablename__ = "players"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_playing = Column(Boolean, default=False)

    games = relationship("GamePlayer", back_populates="player")


class GameStatus(str, enum.Enum):
    waiting = "waiting"
    playing = "playing"
    finished = "finished"


class Game(Base):
    __tablename__ = "games"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(GameStatus), default=GameStatus.waiting)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    winner_id = Column(String, ForeignKey("players.id"), nullable=True)

    players = relationship("GamePlayer", back_populates="game")
    boards = relationship("Board", back_populates="game")


class GamePlayer(Base):
    __tablename__ = "game_players"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"))
    player_id = Column(String, ForeignKey("players.id"))
    is_turn = Column(Boolean, default=False)

    game = relationship("Game", back_populates="players")
    player = relationship("Player", back_populates="games")


class Board(Base):
    __tablename__ = "boards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"))
    player_id = Column(String, ForeignKey("players.id"))
    state = Column(JSON, nullable=False)
    moves = Column(JSON, default=list)

    game = relationship("Game", back_populates="boards")
