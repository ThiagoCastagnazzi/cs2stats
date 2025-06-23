from pydantic import BaseModel
from typing import List, Optional


class PlayerBase(BaseModel):
    id: int
    nickname: str
    picture: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        orm_mode = True


class TeamBase(BaseModel):
    id: int
    name: str
    ranking: int
    points: int
    url: str

    class Config:
        orm_mode = True


class TeamWithPlayers(TeamBase):
    players: List[PlayerBase] = []


class PlayerWithTeam(PlayerBase):
    team: Optional[TeamBase] = None
