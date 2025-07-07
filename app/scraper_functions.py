import random
import re
import time
from typing import Dict, List

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Variáveis globais para a sessão do Playwright
browser_global = None
context_global = None


def init_playwright_session():
    global browser_global, context_global
    if browser_global is None or context_global is None:
        p = sync_playwright().start()
        browser_global = p.firefox.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context_global = browser_global.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            viewport={"width": 1366, "height": 768},
        )


def close_playwright_session():
    global browser_global, context_global
    if browser_global:
        browser_global.close()
        browser_global = None
        context_global = None


def safe_navigate(page, url, timeout=30000):
    """Navega para uma URL de forma segura"""
    try:
        # Pausa aleatória para parecer mais humano
        time.sleep(random.uniform(2, 5))

        page.goto(url, timeout=timeout, wait_until="domcontentloaded")

        # Aguarda carregamento adicional
        time.sleep(random.uniform(3, 6))

        # Verifica se não está bloqueado
        if "Just a moment" in page.title() or "Cloudflare" in page.title():
            print("⚠️ Página bloqueada, aguardando...")
            time.sleep(random.uniform(10, 15))
            return False

        return True

    except Exception as e:
        print(f"Erro ao navegar: {e}")
        return False


def get_team_active_players_and_coach(team_url: str) -> List[Dict]:
    """
    Coleta apenas os 5 jogadores ativos e o coach de um time específico
    """
    print(f"Coletando jogadores ativos e coach de: {team_url}")

    init_playwright_session()
    page = context_global.new_page()

    try:
        if not safe_navigate(page, team_url):
            print("Falha ao carregar página do time")
            return []

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        players_and_coach = []

        # Estratégia 1: Procura por seção de lineup atual
        lineup_section = soup.find(
            "div", class_=["lineup", "team-lineup", "current-lineup"]
        )

        if lineup_section:
            print("Encontrada seção de lineup")
            players_and_coach.extend(extract_from_lineup_section(lineup_section))

        # Estratégia 2: Procura por links de jogadores na página principal
        if not players_and_coach:
            print("Tentando estratégia alternativa...")
            players_and_coach.extend(extract_players_alternative(soup))

        # Limita a 6 pessoas (5 jogadores + 1 coach)
        if len(players_and_coach) > 6:
            players_and_coach = players_and_coach[:6]

        # Identifica quem é coach baseado em padrões comuns
        for person in players_and_coach:
            if is_likely_coach(person["nickname"]):
                person["role"] = "coach"
            else:
                person["role"] = "player"

        # Garante que temos no máximo 5 jogadores
        players = [p for p in players_and_coach if p["role"] == "player"]
        coaches = [p for p in players_and_coach if p["role"] == "coach"]

        if len(players) > 5:
            players = players[:5]

        if len(coaches) > 1:
            coaches = coaches[:1]

        result = players + coaches

        print(f"Coletados: {len(players)} jogadores e {len(coaches)} coach(es)")
        for person in result:
            print(f"  {person["role"]}: {person["nickname"]} (ID: {person["id"]})")

        return result

    except Exception as e:
        print(f"Erro ao coletar jogadores: {e}")
        return []
    finally:
        page.close()


def get_player_stats_page(player_url: str) -> Dict[str, float]:
    """
    Extrai estatísticas detalhadas da página de stats do jogador.
    Exemplo: https://www.hltv.org/stats/players/18765/donk
    """
    import re

    def try_parse(value):
        value = value.replace('%', '').replace(',', '.')
        try:
            return float(value)
        except ValueError:
            try:
                return int(value)
            except ValueError:
                return value

    print(f"📊 Coletando stats: {player_url}")

    stats = {}

    player_id_match = re.search(r"/(?:players|coach)/(\d+)", player_url)
    if not player_id_match:
        print("❌ ID do jogador/coach não encontrado na URL")
        return {}

    player_id = player_id_match.group(1)
    stats_url = f"https://www.hltv.org/stats/players/{player_id}/-"

    init_playwright_session()
    page = context_global.new_page()

    try:
        if not safe_navigate(page, stats_url):
            return {}

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        def extract_stat(label_keywords):
            """
            Procura o valor de uma estatística com base em palavras-chave
            """
            for row in soup.select(".standard-box .stats-row"):
                spans = row.select("span")
                if len(spans) >= 2:
                    label_text = spans[0].text.strip().lower()
                    for keyword in label_keywords:
                        if keyword in label_text:
                            return try_parse(spans[1].text.strip())
            return None

        stats["total_kills"] = extract_stat(["total kills"])
        stats["headshot_percentage"] = extract_stat(["headshot %"])
        stats["total_deaths"] = extract_stat(["total deaths"])
        stats["kd_ratio"] = extract_stat(["k/d ratio"])
        stats["damage_per_round"] = extract_stat(["damage / round"])
        stats["grenade_damage_per_round"] = extract_stat(["grenade dmg / round"])
        stats["maps_played"] = extract_stat(["maps played"])
        stats["rounds_played"] = extract_stat(["rounds played"])
        stats["kills_per_round"] = extract_stat(["kills / round"])
        stats["assists_per_round"] = extract_stat(["assists / round"])
        stats["deaths_per_round"] = extract_stat(["deaths / round"])
        stats["saved_by_teammate_per_round"] = extract_stat(["saved by teammate / round"])
        stats["saved_teammates_per_round"] = extract_stat(["saved teammates / round"])
        rating = extract_stat(["rating"])
        if not rating:
            rating = extract_stat(["rating 2.1"])

        stats["rating"] = rating

        return stats

    except Exception as e:
        print(f"❌ Erro ao coletar stats detalhados: {e}")
        return {}
    finally:
        page.close()


def extract_from_lineup_section(lineup_section):
    """Extrai jogadores da seção de lineup"""
    players = []

    # Procura por links de jogadores na seção
    player_links = lineup_section.find_all(
        "a", href=re.compile(r"/(?:player|coach)/\d+/")
    )

    for link in player_links:
        try:
            href = link.get("href", "")
            if not href:
                continue

            # Extrai ID e nome do jogador
            player_match = re.search(r"/(?:player|coach)/(\d+)/([^/]+)", href)
            if not player_match:
                continue

            player_id = int(player_match.group(1))
            player_name = player_match.group(2)
            player_nickname = link.get_text(strip=True)

            if player_nickname and len(player_nickname) > 1:
                players.append(
                    {
                        "id": player_id,
                        "name": player_name,
                        "nickname": player_nickname,
                        "url": "https://www.hltv.org" + href,
                        "role": "player",  # Será ajustado depois
                    }
                )

        except Exception as e:
            print(f"Erro ao processar link de jogador: {e}")
            continue

    return players


def extract_players_alternative(soup):
    """Método alternativo para extrair jogadores quando não há seção específica"""
    players = []

    # Procura por todos os links de jogadores na página
    player_links = soup.find_all("a", href=re.compile(r"/(?:player|coach)/\d+/"))

    # Remove duplicatas baseado no ID
    seen_ids = set()
    unique_links = []

    for link in player_links:
        href = link.get("href", "")
        player_match = re.search(r"/(?:player|coach)/(\d+)/([^/]+)", href)
        if player_match:
            player_id = int(player_match.group(1))
            if player_id not in seen_ids:
                seen_ids.add(player_id)
                unique_links.append(link)

    # Processa os primeiros 6 links únicos (assumindo 5 jogadores + 1 coach)
    for link in unique_links[:6]:
        try:
            href = link.get("href", "")
            player_match = re.search(r"/(?:player|coach)/(\d+)/([^/]+)", href)
            if not player_match:
                continue

            player_id = int(player_match.group(1))
            player_name = player_match.group(2)
            player_nickname = link.get_text(strip=True)

            if player_nickname and len(player_nickname) > 1:
                players.append(
                    {
                        "id": player_id,
                        "name": player_name,
                        "nickname": player_nickname,
                        "url": "https://www.hltv.org" + href,
                        "role": "player",  # Será ajustado depois
                    }
                )

        except Exception as e:
            print(f"Erro ao processar jogador alternativo: {e}")
            continue

    return players


def is_likely_coach(nickname):
    """Identifica se um nickname provavelmente pertence a um coach"""
    coach_indicators = [
        "coach",
        "manager",
        "head",
        "assistant",
        "staff",
        "zonic",
        "threat",
        "xizt",
        "natu",
        "kassad",  # Coaches conhecidos
        "blade",
        "starix",
        "zeus",
        "ex6tenz",  # Mais coaches conhecidos
    ]

    nickname_lower = nickname.lower()

    # Verifica se contém indicadores de coach
    for indicator in coach_indicators:
        if indicator in nickname_lower:
            return True

    return False


def get_player_details(player_url):
    """
    Extrai detalhes e estatísticas de um jogador ou coach do HLTV.org.
    """
    print(f"Coletando dados detalhados de: {player_url}")

    init_playwright_session()
    page = context_global.new_page()

    try:
        if not safe_navigate(page, player_url):
            return {}

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        data = {}

        # Foto
        picture_elem = soup.find("img", {"class": "bodyshot-img"})
        if not picture_elem:
            picture_elem = soup.find("img", src=re.compile(r"playerbodyshot"))
        if picture_elem:
            data["photo"] = picture_elem.get("src")

        # Nome real
        real_name_elem = soup.find("div", class_="playerRealname")
        if real_name_elem:
            data["real_name"] = real_name_elem.get_text(strip=True)

        # País
        country_elem = soup.find("img", class_="flag")
        if country_elem:
            data["country"] = country_elem.get("title")

        # Idade
        age_text = soup.find("div", class_="playerAge")
        if age_text:
            age_match = re.search(r"(\d+)", age_text.get_text())
            if age_match:
                data["age"] = int(age_match.group(1))

        # Extrai ID e nome do jogador/coach da URL de perfil
        player_id_match = re.search(r"/(?:player|coach)/(\d+)/([^/]+)", player_url)
        if player_id_match:
            player_id = player_id_match.group(1)
            player_name_slug = player_id_match.group(2)
            stats_url = f"https://www.hltv.org/stats/players/{player_id}/{player_name_slug}"
            # Coleta estatísticas detalhadas da página de stats
            stats = get_player_stats_page(stats_url)
            data["stats"] = stats
        else:
            data["stats"] = {}

        # Coleta os troféus/conquistas do jogador
        data["achievements"] = get_player_achievements(soup)

        return data

    except Exception as e:
        print(f"Erro ao coletar detalhes do jogador/coach: {e}")
        return {}

    finally:
        page.close()


def top30_teams():
    """
    Coleta os top 30 times do ranking do HLTV.org com informações adicionais
    """
    print("Coletando ranking dos times do HLTV.org...")

    init_playwright_session()
    page = context_global.new_page()

    try:
        if not safe_navigate(page, "https://www.hltv.org/ranking/teams/"):
            print("Falha ao carregar página de ranking")
            return []

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        ranking_block = soup.find("div", {"class": "ranking"})
        if not ranking_block:
            print("Ranking block não encontrado!")
            return extract_teams_alternative(soup)

        teams = []

        for team in ranking_block.find_all("div", {"class": "ranked-team standard-box"}):
            if len(teams) >= 30:
                break

            try:
                name = team.find("div", class_="ranking-header").select_one(".name").text.strip()
                ranking = int(team.select_one(".position").text.strip().replace("#", ""))

                points_elem = team.find("span", {"class": "points"})
                points = int(points_elem.text.strip("()").split(" ")[0]) if points_elem else 0

                more_div = team.find("div", class_="more")
                team_url = None
                if more_div:
                    profile_link = more_div.find("a", href=re.compile(r"/team/\d+/"))
                    if profile_link:
                        team_url = "https://www.hltv.org" + profile_link["href"]

                team_picture_elem = team.find("span", {"class": "team-logo"}).find("img")
                team_picture_url = team_picture_elem.get("src") if team_picture_elem else None

                if not all([name, ranking, team_url]):
                    continue

                # Coleta informações adicionais da página do time
                team_details = {}
                trophies = []
                stats = {}
                maps_stats = []

                if team_url:
                    try:
                        print(f"Coletando detalhes adicionais de: {team_url}")
                        if safe_navigate(page, team_url):
                            team_html = page.content()
                            team_soup = BeautifulSoup(team_html, "lxml")

                            # Coleta informações básicas do time
                            country_elem = team_soup.find("div", class_="team-country")
                            if country_elem:
                                team_details["country"] = country_elem.text.strip()

                            # Coleta os troféus/conquistas
                            trophies = get_team_achievements(team_soup)

                            # Coleta estatísticas do time
                            stats = get_team_stats(team_soup)

                            maps_stats = get_team_map_stats(team_soup)

                            # Adiciona um delay para evitar bloqueio
                            time.sleep(random.uniform(2, 5))

                    except Exception as e:
                        print(f"Erro ao coletar detalhes do time {name}: {e}")

                teams.append({
                    "name": name,
                    "ranking": ranking,
                    "points": points,
                    "url": team_url,
                    "logo_url": team_picture_url,
                    "details": team_details,
                    "stats": stats,
                    "trophies": trophies,
                    "map_stats": maps_stats,
                    "players": []
                })

                print(f"Time coletado: {name} (#{ranking}) com {len(trophies)} troféus")

            except Exception as e:
                print(f"Erro ao processar time: {e}")
                continue

        print(f"Total de times coletados: {len(teams)}")
        return teams

    except Exception as e:
        print(f"Erro ao coletar ranking: {e}")
        return []
    finally:
        page.close()


def get_team_achievements(team_soup):
    """
    Coleta todas as conquistas/troféus de um time e formata para o modelo TeamAchievement
    Retorna lista de dicionários prontos para criação de objetos TeamAchievement
    """
    achievements = []

    trophy_row = team_soup.find("div", class_="trophyRow")
    if not trophy_row:
        return achievements

    for trophy in trophy_row.find_all(["a", "div"], class_="trophy"):
        try:
            img = trophy.find("img", class_="trophyIcon")
            if not img:
                continue

            # Extrai título e verifica se é um Major
            title_span = trophy.find("span", class_="trophyDescription")
            is_major = "majorTrophy" in title_span.get("class", [])
            title = title_span.get("title", "")

            # Extrai o ano do título
            year = None
            year_match = re.search(r"\b(20\d{2})\b", title)
            if year_match:
                year = int(year_match.group(1))

            # Determina o tier do evento
            event_tier = "S-Tier"  # Valor padrão
            if is_major:
                event_tier = "Major"
            elif "blast" in title.lower():
                event_tier = "S-Tier"
            elif "iem" in title.lower():
                event_tier = "S-Tier"
            elif "esl" in title.lower():
                event_tier = "A-Tier"

            # Formata a URL da imagem
            image_url = img["src"]
            if image_url.startswith("/"):
                image_url = "https://www.hltv.org" + image_url

            achievement_data = {
                "title": title,
                "event_name": title.split(" ")[0] if title else None,  # Nome simplificado do evento
                "year": year,
                "placement": "1st",  # Assume primeiro lugar
                "trophy_image_url": image_url,
                "event_tier": event_tier
            }

            # Se for um link, pega a URL do evento
            if trophy.name == "a" and trophy.has_attr("href"):
                achievement_data["event_url"] = "https://www.hltv.org" + trophy["href"]

            achievements.append(achievement_data)

        except Exception as e:
            print(f"Erro ao processar troféu: {e}")
            continue

    return achievements


def get_player_achievements(player_soup):
    """
    Coleta todas as conquistas/troféus de um jogador e formata para o modelo PlayerAchievement
    Retorna lista de dicionários prontos para criação de objetos PlayerAchievement

    Args:
        player_soup: BeautifulSoup object da página do jogador

    Returns:
        Lista de dicionários com informações dos troféus
    """
    achievements = []

    trophy_row = player_soup.find("div", class_="trophyRow")
    if not trophy_row:
        return achievements

    for trophy in trophy_row.find_all(["a", "div"], class_="trophy"):
        try:
            img = trophy.find("img", class_="trophyIcon")
            if not img:
                continue

            # Extrai título e verifica se é um Major
            title_span = trophy.find("span", class_="trophyDescription")
            is_major = "majorTrophy" in title_span.get("class", []) if title_span else False
            title = title_span.get("title", "") if title_span else ""

            # Extrai o ano do título (se for um prêmio anual)
            year = None
            award_year = trophy.find("span", class_="award-year")
            if award_year:
                year = int(award_year.text.strip().replace("'", "20"))
            else:
                year_match = re.search(r"\b(20\d{2})\b", title)
                if year_match:
                    year = int(year_match.group(1))

            # Determina o tipo de conquista
            achievement_type = "tournament"  # Padrão para torneios
            if "best player" in title.lower() or "award" in title.lower():
                achievement_type = "individual_award"
            elif "igl of the year" in title.lower():
                achievement_type = "panel_award"

            # Determina o tier do evento (para torneios)
            event_tier = "S-Tier"  # Valor padrão
            if is_major:
                event_tier = "Major"
            elif "blast" in title.lower():
                event_tier = "S-Tier"
            elif "iem" in title.lower():
                event_tier = "S-Tier"
            elif "esl" in title.lower():
                event_tier = "A-Tier"
            elif "dreamhack" in title.lower():
                event_tier = "A-Tier"

            # Formata a URL da imagem
            image_url = img["src"]
            if image_url.startswith("/"):
                image_url = "https://www.hltv.org" + image_url

            achievement_data = {
                "title": title,
                "event_name": title.split(" ")[0] if title else None,
                "year": year,
                "achievement_type": achievement_type,
                "trophy_image_url": image_url,
                "event_tier": event_tier if achievement_type == "tournament" else None,
                "placement": "1st" if achievement_type == "tournament" else None,
                "individual_award_type": achievement_type if achievement_type != "tournament" else None
            }

            # Se for um link, pega a URL do evento
            if trophy.name == "a" and trophy.has_attr("href"):
                achievement_data["event_url"] = "https://www.hltv.org" + trophy["href"]

            achievements.append(achievement_data)

        except Exception as e:
            print(f"Erro ao processar troféu do jogador: {e}")
            continue

    return achievements


def get_team_stats(team_soup):
    """
    Coleta estatísticas do time como win rate, etc.
    """
    stats = {
        'win_rate': None,
    }

    try:
        matches_tab = team_soup.find("div", {"id": "matchesBox"})
        if not matches_tab:
            return stats

        win_rate_div = matches_tab.findAll("div", class_="highlighted-stat")[1]
        if win_rate_div:
            stat_div = win_rate_div.find("div", class_="stat")
            stats['win_rate'] = float(stat_div.text.strip().replace('%', ''))

        stats_tab = team_soup.find("div", {"id": "statsBox"})
        if not stats_tab:
            return stats


    except Exception as e:
        print(f"Erro ao coletar estatísticas do time: {e}")

    return stats


def get_team_map_stats(team_soup):
    """
    Coleta estatísticas dos mapas do time a partir do HTML
    Retorna lista de dicionários com os dados dos mapas
    """
    maps = []

    try:
        map_stats_div = team_soup.find("div", {"class": "map-statistics"})
        if not map_stats_div:
            return maps

        for map_container in map_stats_div.find_all("div", {"class": "map-statistics-container"}):
            try:
                # Informações básicas do mapa
                map_row = map_container.find("div", {"class": "map-statistics-row"})
                map_name = map_row.find("div", {"class": "map-statistics-row-map-mapname"}).text.strip()
                win_percentage = float(
                    map_row.find("div", {"class": "map-statistics-row-win-percentage"}).text.strip('%'))

                # Informações estendidas (podem estar ocultas)
                extended_div = map_container.find("div", {"class": "map-statistics-extended"})

                # Win/Draw/Loss
                wdl = extended_div.find("div", {"class": "map-statistics-extended-wdl"})
                wins = int(wdl.find_all("div", {"class": "stat"})[0].text.strip())
                draws = int(wdl.find_all("div", {"class": "stat"})[1].text.strip())
                losses = int(wdl.find_all("div", {"class": "stat"})[2].text.strip())

                # Estatísticas gerais
                general_stats = {}
                for stat in extended_div.find_all("div", {"class": "map-statistics-extended-general-stat"}):
                    stat_name = stat.find("div").text.strip()
                    stat_value = stat.find_all("div")[1].text.strip('%')
                    general_stats[stat_name] = float(stat_value) if '%' in stat.find_all("div")[1].text else stat_value

                # Veto data
                veto_data = {}
                veto_container = extended_div.find("div", {"class": "map-statistics-extended-highlight-veto-container"})
                if veto_container:
                    picks_text = \
                    veto_container.find_all("div", {"class": "map-statistics-extended-highlight-veto"})[0].find_all(
                        "div")[1].text
                    bans_text = \
                    veto_container.find_all("div", {"class": "map-statistics-extended-highlight-veto"})[1].find_all(
                        "div")[1].text

                    veto_data["picks_percentage"] = float(picks_text.split('%')[0]) if '%' in picks_text else 0
                    veto_data["bans_percentage"] = float(bans_text.split('%')[0]) if '%' in bans_text else 0

                # Calcular rounds totais e win rates
                total_rounds = wins + draws + losses
                round_win_rate = (wins / total_rounds * 100) if total_rounds > 0 else 0

                # Separar CT e T rounds (simplificado - na prática precisaria de scraping mais detalhado)
                ct_rounds = int(wins * 0.6)  # Aproximação - ajuste conforme dados reais
                t_rounds = wins - ct_rounds
                ct_win_rate = (ct_rounds / wins * 100) if wins > 0 else 0
                t_win_rate = (t_rounds / wins * 100) if wins > 0 else 0

                maps.append({
                    "map_name": map_name,
                    "matches_played": total_rounds,
                    "matches_won": wins,
                    "win_rate": win_percentage,
                    "rounds_played": total_rounds * 30,  # Aproximação - 30 rounds por partida
                    "rounds_won": wins * 16,  # Aproximação - 16 rounds para vencer
                    "round_win_rate": round_win_rate,
                    "ct_rounds_won": ct_rounds,
                    "t_rounds_won": t_rounds,
                    "ct_win_rate": ct_win_rate,
                    "t_win_rate": t_win_rate,
                    "general_stats": general_stats,
                    "veto_data": veto_data
                })

            except Exception as e:
                print(f"Erro ao processar mapa: {e}")
                continue

    except Exception as e:
        print(f"Erro ao coletar estatísticas dos mapas do time: {e}")

    return maps


def extract_teams_alternative(soup):
    """
    Método alternativo para extrair times quando a estrutura padrão não funciona
    """
    print("Tentando método alternativo de extração...")

    teams = []
    # Implementação de um método alternativo, se necessário
    return teams


# Adicione estas funções de parse para evitar erros de NameError
def try_parse_float(value):
    try:
        return float(value.replace("%", "").replace(",", "."))
    except:
        return None


def try_parse_int(value):
    try:
        return int(value.replace(".", ""))
    except:
        return None
