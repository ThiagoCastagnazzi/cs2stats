from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
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
    real_name = Column(String)  # Nome real do jogador
    url = Column(String)
    team_id = Column(Integer, ForeignKey('teams.id'))
    role = Column(String)  # 'player' ou 'coach'

    team = relationship("Team", back_populates="players")

    stats = relationship(
        "PlayerStats",
        back_populates="player",  # Isso deve corresponder ao nome em PlayerStats
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )


class PlayerStats(Base):
    __tablename__ = 'player_stats'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), unique=True)

    picture = Column(String)
    country = Column(String)
    age = Column(Integer)

    total_kills = Column(Integer)
    total_deaths = Column(Integer)
    headshot_percentage = Column(Float)
    kd_ratio = Column(Float)
    damage_per_round = Column(Float)
    grenade_damage_per_round = Column(Float)
    maps_played = Column(Integer)
    rounds_played = Column(Integer)
    kills_per_round = Column(Float)
    assists_per_round = Column(Float)
    deaths_per_round = Column(Float)
    saved_by_teammate_per_round = Column(Float)
    saved_teammates_per_round = Column(Float)
    rating = Column(Float)

    last_updated = Column(DateTime, default=datetime.utcnow)

    player = relationship(
        "Player",
        back_populates="stats"
    )
