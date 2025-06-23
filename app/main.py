from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, banco

app = FastAPI()


def get_db():
    db = banco.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/teams/")
def read_teams(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    return teams


@app.get("/teams/{team_id}/players")
def read_team_players(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return team.players


@app.get("/players/")
def read_players(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    players = db.query(models.Player).offset(skip).limit(limit).all()
    return players


@app.get("/home/")
def read_home():
    return {"message": "Hello World"}
