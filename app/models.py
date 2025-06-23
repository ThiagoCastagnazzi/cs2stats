from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.banco import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    ranking = Column(Integer)
    points = Column(Integer)

    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    url = Column(String)
    team_id = Column(Integer, ForeignKey('teams.id'))

    team = relationship("Team", back_populates="players")

    stats = relationship(
        "PlayerStats",
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )


class PlayerStats(Base):
    __tablename__ = 'player_stats'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    picture = Column(String)
    rating = Column(Float)

    player = relationship("Player", back_populates="stats")
