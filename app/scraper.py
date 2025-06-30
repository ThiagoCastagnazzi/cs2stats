import random
import time
from datetime import datetime

import models
from banco import SessionLocal, engine
from logger import logger
from scraper_functions import (
    top30_teams,
    get_player_details,
    get_team_active_players_and_coach
)

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()


def reset_team_rankings():
    """Reseta rankings e pontos dos times"""
    logger.info("🔄 Resetando rankings e pontos dos times...")
    db.query(models.Team).update({models.Team.ranking: 0, models.Team.points: 0})
    db.commit()
    logger.info("✅ Rankings resetados.")


def get_or_create_player(session, player_id, defaults=None):
    """Obtém ou cria um jogador no banco de dados"""
    instance = session.query(models.Player).filter_by(id=player_id).first()
    if instance:
        return instance, False
    else:
        params = defaults or {}
        params["id"] = player_id
        instance = models.Player(**params)
        session.add(instance)
        return instance, True


def save_teams_with_active_players():
    """
    Coleta e salva times com apenas jogadores ativos e coach do HLTV.org
    """
    logger.info("🚀 Iniciando coleta dos times com jogadores ativos e coach do HLTV.org...")

    try:
        # Coleta times do ranking
        teams = top30_teams()

        if not teams:
            logger.error("❌ Nenhum time foi coletado do HLTV.org")
            return False

        logger.info(f"📊 {len(teams)} times coletados do HLTV.org")

        for i, t in enumerate(teams, 1):
            logger.info(f"💾 [{i}/{len(teams)}] Processando time: {t["name"]} (#{t["ranking"]})")

            try:
                # Busca ou cria o time
                team = db.query(models.Team).filter_by(name=t["name"]).first()
                if not team:
                    team = models.Team(
                        name=t["name"],
                        url=t["url"],
                        ranking=t["ranking"],
                        points=t["points"]
                    )
                    db.add(team)
                    logger.info(f"   ➕ Novo time criado: {t["name"]}")
                else:
                    # Atualiza informações do time
                    team.ranking = t["ranking"]
                    team.points = t["points"]
                    team.url = t["url"]
                    logger.info(f"   🔄 Time atualizado: {t["name"]}")

                db.commit()
                db.refresh(team)

                db.commit()

                # Coleta jogadores ativos e coach do time
                if t["url"]:
                    logger.info(f"   👥 Coletando jogadores ativos e coach de {t["name"]}...")

                    try:
                        active_players_and_coach = get_team_active_players_and_coach(t["url"])

                        if active_players_and_coach:
                            logger.info(f"   📊 {len(active_players_and_coach)} pessoas encontradas")

                            for person in active_players_and_coach:
                                role_emoji = "👤" if person["role"] == "player" else "🎯"
                                logger.info(
                                    f"      {role_emoji} Processando {person["role"]}: {person["nickname"]} (ID: {person["id"]})")

                                try:
                                    player, created = get_or_create_player(
                                        db,
                                        person["id"],
                                        {
                                            "nickname": person["nickname"],
                                            "real_name": person["name"],
                                            "url": person["url"],
                                            "team_id": team.id,
                                            "role": person["role"],
                                        }
                                    )
                                    # Não commitar aqui, o commit será feito no final do loop do time
                                    if created:
                                        logger.info(f"         ➕ Novo {person["role"]} criado: {person["nickname"]}")
                                    else:
                                        logger.info(f"         🔄 {person["role"]} atualizado: {person["nickname"]}")

                                except Exception as e:
                                    logger.error(
                                        f"         ❌ Erro ao processar {person["role"]} {person["nickname"]}: {e}")
                                    db.rollback()
                                    continue
                            db.commit()  # Commit all players for the current team
                        else:
                            logger.warning(f"   ⚠️ Nenhum jogador ativo encontrado para {t["name"]}")

                    except Exception as e:
                        logger.error(f"   ❌ Erro ao coletar jogadores de {t["name"]}: {e}")

                # Pausa entre times para não sobrecarregar o HLTV.org
                if i < len(teams):
                    delay = random.uniform(10, 20)
                    logger.info(f"   ⏳ Aguardando {delay:.1f}s antes do próximo time...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"❌ Erro ao processar time {t["name"]}: {e}")
                db.rollback()
                continue

        logger.info("✅ Times com jogadores ativos e coach salvos com sucesso!")
        return True

    except Exception as e:
        logger.error(f"❌ Erro crítico ao salvar times: {e}")
        return False


def update_active_player_stats(player_id=None, force_update=False, max_players=None):
    """
    Atualiza estatísticas apenas dos jogadores ativos coletando dados do HLTV.org

    Args:
        player_id: ID específico do jogador (None para todos)
        force_update: Força atualização mesmo se dados são recentes
        max_players: Limite máximo de jogadores para processar
    """
    logger.info("🔄 Iniciando atualização de estatísticas dos jogadores ativos...")

    if player_id:
        players = db.query(models.Player).filter_by(id=player_id).all()
        logger.info(f"🎯 Atualizando jogador específico: ID {player_id}")
    else:
        query = db.query(models.Player).filter(
            models.Player.url.isnot(None),
            # Removido filtro por role == 'player' para incluir coaches
        )
        if max_players:
            query = query.limit(max_players)
        players = query.all()
        logger.info(f"📊 Atualizando estatísticas de {len(players)} pessoas ativas...")

    success_count = 0
    error_count = 0
    skipped_count = 0

    for i, player in enumerate(players, 1):
        logger.info(f"🔍 [{i}/{len(players)}] Atualizando estatísticas de {player.nickname} ({player.role})...")

        # Verifica se precisa atualizar
        if not force_update and player.stats:
            logger.info(f"   ⏭️ {player.nickname} já tem estatísticas, pulando...")
            skipped_count += 1
            continue

        if not player.url:
            logger.warning(f"   ⚠️ {player.nickname} não tem URL, pulando...")
            skipped_count += 1
            continue

        try:
            player_data = get_player_details(player.url)
            if not player_data:
                logger.warning(f"   ⚠️ Nenhum dado coletado para {player.nickname}")
                error_count += 1
                continue

            # Cria ou atualiza estatísticas
            if not player.stats:
                player.stats = models.PlayerStats(player_id=player.id)
                db.add(player.stats)

            # Atualiza todos os campos
            stats = player.stats
            stats.picture = player_data.get("photo")
            stats.real_name = player_data.get("real_name")
            stats.country = player_data.get("country")
            stats.age = player_data.get("age")

            if "stats" in player_data:
                stats_data = player_data["stats"]
                stats.total_kills = stats_data.get("total_kills")
                stats.total_deaths = stats_data.get("total_deaths")
                stats.headshot_percentage = stats_data.get("headshot_percentage")
                stats.kd_ratio = stats_data.get("kd_ratio")
                stats.damage_per_round = stats_data.get("damage_per_round")
                stats.grenade_damage_per_round = stats_data.get("grenade_damage_per_round")
                stats.maps_played = stats_data.get("maps_played")
                stats.rounds_played = stats_data.get("rounds_played")
                stats.kills_per_round = stats_data.get("kills_per_round")
                stats.assists_per_round = stats_data.get("assists_per_round")
                stats.deaths_per_round = stats_data.get("deaths_per_round")
                stats.saved_by_teammate_per_round = stats_data.get("saved_by_teammate_per_round")
                stats.saved_teammates_per_round = stats_data.get("saved_teammates_per_round")
                stats.rating = stats_data.get("rating")

            db.commit()
            db.refresh(player.stats)
            success_count += 1

            stats_info = []
            if player_data.get("rating"):
                stats_info.append(f"rating: {player_data["rating"]}")
            if player_data.get("photo"):
                stats_info.append("foto: ✅")

            logger.info(f"   ✅ {player.nickname} atualizado com sucesso!")
            if stats_info:
                logger.info(f"   📊 Dados coletados: {", ".join(stats_info)}")

            # Pausa entre jogadores para não sobrecarregar o HLTV.org
            delay = random.uniform(15, 25)
            logger.info(f"   ⏳ Aguardando {delay:.1f}s antes do próximo jogador...")
            time.sleep(delay)

        except Exception as e:
            error_count += 1
            logger.error(f"   ❌ Erro ao atualizar {player.nickname}: {str(e)}")
            db.rollback()

            # Pausa maior em caso de erro
            time.sleep(random.uniform(20, 30))
            continue

    logger.info(f"✅ Atualização de estatísticas concluída!")
    logger.info(f"   📊 Sucessos: {success_count}")
    logger.info(f"   ❌ Erros: {error_count}")
    logger.info(f"   ⏭️ Pulados: {skipped_count}")


def full_update_active_only(max_players_stats=None):
    """
    Executa atualização completa coletando apenas jogadores ativos e coach do HLTV.org

    Args:
        max_players_stats: Limite de jogadores para atualizar estatísticas (None = todos)
    """
    logger.info("🚀 INICIANDO ATUALIZAÇÃO COMPLETA - APENAS JOGADORES ATIVOS E COACH")
    logger.info("=" * 70)

    start_time = datetime.utcnow()

    try:
        # Fase 1: Coleta times com jogadores ativos e coach do HLTV.org
        logger.info("📋 FASE 1: Coletando times com jogadores ativos e coach do HLTV.org...")
        if not save_teams_with_active_players():
            logger.error("❌ Falha na coleta de times. Continuando com dados existentes...")

        # Fase 2: Atualiza estatísticas apenas dos jogadores ativos do HLTV.org
        logger.info("📊 FASE 2: Atualizando estatísticas dos jogadores ativos do HLTV.org...")
        update_active_player_stats(max_players=max_players_stats)

        end_time = datetime.utcnow()
        duration = end_time - start_time

        logger.info("=" * 70)
        logger.info("🎉 ATUALIZAÇÃO COMPLETA FINALIZADA!")
        logger.info(f"📊 Fonte de dados: HLTV.org exclusivamente")
        logger.info(f"🎯 Foco: Apenas jogadores ativos (5) e coach de cada time")
        logger.info(f"⏱️ Tempo total: {duration}")
        logger.info("=" * 70)

        return True

    except Exception as e:
        logger.error(f"❌ Erro crítico durante atualização: {e}")
        return False


def quick_update_active_only():
    """
    Executa atualização rápida apenas dos times com jogadores ativos e coach do HLTV.org
    """
    logger.info("⚡ INICIANDO ATUALIZAÇÃO RÁPIDA - APENAS JOGADORES ATIVOS E COACH...")

    try:
        if save_teams_with_active_players():
            logger.info("✅ Atualização rápida concluída!")
            return True
        else:
            logger.error("❌ Falha na atualização rápida")
            return False

    except Exception as e:
        logger.error(f"❌ Erro na atualização rápida: {e}")
        return False


def show_active_players_summary():
    """
    Mostra resumo dos jogadores ativos no banco de dados
    """
    logger.info("📊 RESUMO DOS JOGADORES ATIVOS")
    logger.info("=" * 50)

    try:
        teams = db.query(models.Team).order_by(models.Team.ranking).all()

        for team in teams:
            active_players = db.query(models.Player).filter_by(
                team_id=team.id,
            ).all()

            if active_players:
                logger.info(f"\n🏆 {team.name} (#{team.ranking})")

                players = [p for p in active_players if p.role == "player"]
                coaches = [p for p in active_players if p.role == "coach"]

                for player in players:
                    rating = "N/A"
                    if player.stats and player.stats.rating:
                        rating = f"{player.stats.rating:.2f}"
                    logger.info(f"   👤 {player.nickname} (Rating: {rating})")

                for coach in coaches:
                    logger.info(f"   🎯 {coach.nickname} (Coach)")

                logger.info(f"   📊 Total: {len(players)} jogadores + {len(coaches)} coach(es)")

        total_active = db.query(models.Player).filter_by().count()
        total_players = db.query(models.Player).filter_by(role="player").count()
        total_coaches = db.query(models.Player).filter_by(role="coach").count()

        logger.info("\n" + "=" * 50)
        logger.info(f"📈 TOTAIS GERAIS:")
        logger.info(f"   👤 Jogadores ativos: {total_players}")
        logger.info(f"   🎯 Coaches ativos: {total_coaches}")
        logger.info(f"   📊 Total de pessoas ativas: {total_active}")

    except Exception as e:
        logger.error(f"❌ Erro ao gerar resumo: {e}")


if __name__ == "__main__":
    logger.info("🎯 Sistema de Scraping HLTV.org - Apenas Jogadores Ativos e Coach")
    logger.info("📊 Fonte de dados: HLTV.org exclusivamente")
    logger.info("🎯 Foco: 5 jogadores ativos + 1 coach por time")
    logger.info("🚀 Iniciando coleta completa e atualização...")

    # Coleta times + jogadores ativos + estatísticas já salvas junto
    if full_update_active_only():
        logger.info("✅ Coleta e atualização concluídas com sucesso!")
    else:
        logger.error("❌ Falha na coleta e atualização")

    # Mostra resumo final
    show_active_players_summary()
