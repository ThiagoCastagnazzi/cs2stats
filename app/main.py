from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, banco
from swagger_docs import custom_openapi

app = FastAPI(
    title="Sistema HLTV Expandido API",
    description="API para acessar dados de times e jogadores de Counter-Strike 2",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar documentação customizada
app.openapi = lambda: custom_openapi(app)


def get_db():
    db = banco.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["Home"])
def read_home():
    """Endpoint de boas-vindas da API"""
    return {"message": "Bem-vindo à API do Sistema HLTV Expandido"}


# Rotas para Times
@app.get("/teams/", tags=["Teams"], response_model=List[dict])
def read_teams(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os times.

    - **skip**: Número de registros a pular (paginação)
    - **limit**: Número máximo de registros a retornar
    """
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    return [
        {
            "id": team.id,
            "name": team.name,
            "url": team.url,
            "ranking": team.ranking,
            "points": team.points
        }
        for team in teams
    ]


@app.get("/teams/{team_id}", tags=["Teams"])
def read_team(team_id: int, db: Session = Depends(get_db)):
    """
    Retorna informações detalhadas de um time específico.

    - **team_id**: ID do time
    """
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    return {
        "id": team.id,
        "name": team.name,
        "url": team.url,
        "ranking": team.ranking,
        "points": team.points
    }


@app.get("/teams/{team_id}/players", tags=["Teams"])
def read_team_players(team_id: int, db: Session = Depends(get_db)):
    """
    Retorna todos os jogadores de um time específico.

    - **team_id**: ID do time
    """
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    return [
        {
            "id": player.id,
            "nickname": player.nickname,
            "real_name": player.real_name,
            "url": player.url,
            "role": player.role,
            "team_id": player.team_id
        }
        for player in team.players
    ]


# Rotas para Jogadores
@app.get("/players/", tags=["Players"])
def read_players(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os jogadores.

    - **skip**: Número de registros a pular (paginação)
    - **limit**: Número máximo de registros a retornar
    """
    players = db.query(models.Player).offset(skip).limit(limit).all()
    return [
        {
            "id": player.id,
            "nickname": player.nickname,
            "real_name": player.real_name,
            "url": player.url,
            "role": player.role,
            "team_id": player.team_id,
            "team_name": player.team.name if player.team else None
        }
        for player in players
    ]


@app.get("/players/{player_id}", tags=["Players"])
def read_player(player_id: int, db: Session = Depends(get_db)):
    """
    Retorna informações detalhadas de um jogador específico.

    - **player_id**: ID do jogador
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    return {
        "id": player.id,
        "nickname": player.nickname,
        "real_name": player.real_name,
        "url": player.url,
        "role": player.role,
        "team_id": player.team_id,
        "team_name": player.team.name if player.team else None
    }


@app.get("/players/{player_id}/stats", tags=["Player Stats"])
def read_player_stats(player_id: int, db: Session = Depends(get_db)):
    """
    Retorna as estatísticas detalhadas de um jogador específico.

    - **player_id**: ID do jogador
    """
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    if not player.stats:
        raise HTTPException(status_code=404, detail="Estatísticas não encontradas para este jogador")

    stats = player.stats
    return {
        "player_id": player.id,
        "player_nickname": player.nickname,
        "picture": stats.picture,
        "country": stats.country,
        "age": stats.age,
        "total_kills": stats.total_kills,
        "total_deaths": stats.total_deaths,
        "headshot_percentage": stats.headshot_percentage,
        "kd_ratio": stats.kd_ratio,
        "damage_per_round": stats.damage_per_round,
        "grenade_damage_per_round": stats.grenade_damage_per_round,
        "maps_played": stats.maps_played,
        "rounds_played": stats.rounds_played,
        "kills_per_round": stats.kills_per_round,
        "assists_per_round": stats.assists_per_round,
        "deaths_per_round": stats.deaths_per_round,
        "saved_by_teammate_per_round": stats.saved_by_teammate_per_round,
        "saved_teammates_per_round": stats.saved_teammates_per_round,
        "rating": stats.rating,
        "last_updated": stats.last_updated
    }


# Rotas para Estatísticas
@app.get("/stats/players", tags=["Player Stats"])
def read_all_player_stats(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Retorna estatísticas de todos os jogadores.

    - **skip**: Número de registros a pular (paginação)
    - **limit**: Número máximo de registros a retornar
    """
    stats = db.query(models.PlayerStats).offset(skip).limit(limit).all()
    return [
        {
            "player_id": stat.player_id,
            "player_nickname": stat.player.nickname if stat.player else None,
            "picture": stat.picture,
            "country": stat.country,
            "age": stat.age,
            "total_kills": stat.total_kills,
            "total_deaths": stat.total_deaths,
            "headshot_percentage": stat.headshot_percentage,
            "kd_ratio": stat.kd_ratio,
            "damage_per_round": stat.damage_per_round,
            "grenade_damage_per_round": stat.grenade_damage_per_round,
            "maps_played": stat.maps_played,
            "rounds_played": stat.rounds_played,
            "kills_per_round": stat.kills_per_round,
            "assists_per_round": stat.assists_per_round,
            "deaths_per_round": stat.deaths_per_round,
            "saved_by_teammate_per_round": stat.saved_by_teammate_per_round,
            "saved_teammates_per_round": stat.saved_teammates_per_round,
            "rating": stat.rating,
            "last_updated": stat.last_updated
        }
        for stat in stats
    ]


# Rotas de busca e filtros
@app.get("/players/search", tags=["Players"])
def search_players(
        nickname: Optional[str] = None,
        team_id: Optional[int] = None,
        role: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    Busca jogadores por critérios específicos.

    - **nickname**: Busca por apelido (busca parcial)
    - **team_id**: Filtra por ID do time
    - **role**: Filtra por função (player, coach, etc.)
    """
    query = db.query(models.Player)

    if nickname:
        query = query.filter(models.Player.nickname.ilike(f"%{nickname}%"))

    if team_id:
        query = query.filter(models.Player.team_id == team_id)

    if role:
        query = query.filter(models.Player.role == role)

    players = query.all()

    return [
        {
            "id": player.id,
            "nickname": player.nickname,
            "real_name": player.real_name,
            "url": player.url,
            "role": player.role,
            "team_id": player.team_id,
            "team_name": player.team.name if player.team else None
        }
        for player in players
    ]


@app.get("/teams/search", tags=["Teams"])
def search_teams(
        name: Optional[str] = None,
        ranking_min: Optional[int] = None,
        ranking_max: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Busca times por critérios específicos.

    - **name**: Busca por nome (busca parcial)
    - **ranking_min**: Ranking mínimo
    - **ranking_max**: Ranking máximo
    """
    query = db.query(models.Team)

    if name:
        query = query.filter(models.Team.name.ilike(f"%{name}%"))

    if ranking_min:
        query = query.filter(models.Team.ranking >= ranking_min)

    if ranking_max:
        query = query.filter(models.Team.ranking <= ranking_max)

    teams = query.all()

    return [
        {
            "id": team.id,
            "name": team.name,
            "url": team.url,
            "ranking": team.ranking,
            "points": team.points
        }
        for team in teams
    ]


# Rota de estatísticas gerais
@app.get("/stats/summary", tags=["Stats"])
def get_stats_summary(db: Session = Depends(get_db)):
    """
    Retorna um resumo das estatísticas gerais do sistema.
    """
    total_teams = db.query(models.Team).count()
    total_players = db.query(models.Player).count()
    total_stats = db.query(models.PlayerStats).count()

    return {
        "total_teams": total_teams,
        "total_players": total_players,
        "total_player_stats": total_stats,
        "coverage_percentage": round((total_stats / total_players * 100) if total_players > 0 else 0, 2)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

