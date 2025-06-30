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
        stats["rating"] = extract_stat(["rating 2.0"])

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

        return data

    except Exception as e:
        print(f"Erro ao coletar detalhes do jogador/coach: {e}")
        return {}

    finally:
        page.close()


def top30_teams():
    """
    Coleta os top 30 times do ranking do HLTV.org
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

        # Procura pelo bloco de ranking
        ranking_block = soup.find("div", {"class": "ranking"})
        if not ranking_block:
            print("Ranking block não encontrado!")
            # Tenta estrutura alternativa
            return extract_teams_alternative(soup)

        teams = []

        for team in ranking_block.find_all(
                "div", {"class": "ranked-team standard-box"}
        ):
            if len(teams) >= 30:
                break

            try:
                # Nome do time
                name_elem = team.find("div", class_="ranking-header").select_one(
                    ".name"
                )
                if not name_elem:
                    continue
                name = name_elem.text.strip()

                # Ranking
                ranking_elem = team.select_one(".position")
                if not ranking_elem:
                    continue
                ranking = int(ranking_elem.text.strip().replace("#", ""))

                # Pontos
                points = 0
                points_elem = team.find("span", {"class": "points"})
                if points_elem:
                    points_text = points_elem.text.strip("()").split(" ")[0]
                    points = int(points_text) or 0

                # URL do time
                team_page_link = team.find("a", href=re.compile(r"/team/\d+/"))
                if team_page_link:
                    team_url = "https://www.hltv.org" + team_page_link["href"]

                if name and ranking and team_url:
                    teams.append(
                        {
                            "name": name,
                            "ranking": ranking,
                            "points": points,
                            "url": team_url,
                            "players": [],  # Será preenchido depois
                        }
                    )

                    print(f"Time coletado: {name} (#{ranking})")

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
