from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.banco import Base


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
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
    achievements = relationship("PlayerAchievement", back_populates="player", cascade="all, delete-orphan")


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


class PlayerAchievement(Base):
    __tablename__ = 'player_achievements'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))

    title = Column(String)
    event_name = Column(String)
    year = Column(Integer)
    placement = Column(String)
    prize_money = Column(String)
    trophy_image_url = Column(String)
    event_tier = Column(String)
    mvp_award = Column(String)

    player = relationship("Player", back_populates="achievements")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    ranking = Column(Integer)
    points = Column(Integer)

    logo_url = Column(String)
    region = Column(String)
    win_rate = Column(Float)
    weeks_in_top30 = Column(Integer)
    average_player_age = Column(Float)
    coach_name = Column(String)
    peak_ranking = Column(Integer)
    time_at_peak = Column(String)

    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")
    achievements = relationship("TeamAchievement", back_populates="team", cascade="all, delete-orphan")
    map_stats = relationship("TeamMapStats", back_populates="team", cascade="all, delete-orphan")


class TeamAchievement(Base):
    __tablename__ = 'team_achievements'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))

    title = Column(String)
    event_name = Column(String)
    year = Column(Integer)
    placement = Column(String)
    prize_money = Column(String)
    trophy_image_url = Column(String)
    event_tier = Column(String)

    team = relationship("Team", back_populates="achievements")


class TeamMapStats(Base):
    __tablename__ = 'team_map_stats'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))

    map_name = Column(String)
    matches_played = Column(Integer)
    matches_won = Column(Integer)
    win_rate = Column(Float)
    rounds_played = Column(Integer)
    rounds_won = Column(Integer)
    round_win_rate = Column(Float)
    ct_rounds_won = Column(Integer)
    t_rounds_won = Column(Integer)
    ct_win_rate = Column(Float)
    t_win_rate = Column(Float)

    team = relationship("Team", back_populates="map_stats")
