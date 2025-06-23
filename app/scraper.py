import models
from banco import SessionLocal, engine
from logger import logger
from scraper_functions import top30_teams, get_player_details

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()


def reset_team_rankings():
    logger.info("🔄 Resetando rankings e pontos dos times...")
    db.query(models.Team).update({models.Team.ranking: 0, models.Team.points: 0})
    db.commit()
    logger.info("✅ Rankings resetados.")


def get_or_create_player(session, player_id, defaults=None):
    instance = session.query(models.Player).filter_by(id=player_id).first()
    if instance:
        return instance, False
    else:
        params = defaults or {}
        params['id'] = player_id
        instance = models.Player(**params)
        session.add(instance)
        return instance, True


def save_teams():
    logger.info("Iniciando salvamento dos times...")
    teams = top30_teams()

    for t in teams:
        logger.info(f"Processando time: {t['name']}")
        team = db.query(models.Team).filter_by(name=t['name']).first()
        if not team:
            team = models.Team(
                name=t['name'],
                url=t['url'],
                ranking=t['ranking'],
                points=t['points']
            )
            db.add(team)
            db.commit()
            db.refresh(team)

        for p in t['players']:
            logger.info(f" -> Processando jogador: {p['nickname']}")

            player, created = get_or_create_player(db, player_id=p['id'], defaults={
                "nickname": p['nickname'],
                "url": p['url'],
                "team_id": team.id
            })

            details = get_player_details(p['url'])
            player.team_id = team.id

            if player.stats:
                stats = player.stats
            else:
                stats = models.PlayerStats()
                player.stats = stats

            stats.picture = details.get("picture")
            stats.rating = float(details.get("rating") or 0)

            db.add(player)

    db.commit()


if __name__ == "__main__":
    reset_team_rankings()
    save_teams()
