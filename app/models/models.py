import enum
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_playing = Column(Boolean, default=False)

    # games = relationship("GamePlayer", back_populates="player")


class GameStatus(str, enum.Enum):
    waiting = "waiting"
    playing = "playing"
    finished = "finished"


class Game(Base):
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player1_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    player2_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    board1 = Column(JSON)
    board2 = Column(JSON)
    status = Column(Enum(GameStatus), default=GameStatus.waiting)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), server_default=func.now())

    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])
    winner = relationship("Player", foreign_keys=[winner_id])


# class GamePlayer(Base):
#     __tablename__ = "game_players"
#     id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     game_id = Column(String, ForeignKey("games.id"))
#     player_id = Column(String, ForeignKey("players.id"))
#     is_turn = Column(Boolean, default=False)
#
#     game = relationship("Game", back_populates="players")
#     player = relationship("Player", back_populates="games")


# class Board(Base):
#     __tablename__ = "boards"
#     id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
#     game_id = Column(String, ForeignKey("games.id"))
#     state = Column(JSON, nullable=False)
#     moves = Column(JSON, default=list)
#
#     game = relationship("Game", back_populates="boards")
