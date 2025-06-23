import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def get_player_details(player_url):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(player_url)

        try:
            page.wait_for_selector("img.bodyshot-img", timeout=1000)
        except:
            print("Timeout esperando a imagem do jogador")

        time.sleep(1)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")

    picture = soup.find("img", {"class": "bodyshot-img"})
    picture_url = picture["src"] if picture else None
    rating = soup.find("span", {"class": "statsVal"}).find('p').text

    return {
        "picture": picture_url,
        "rating": rating,
    }


def try_parse_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def top30_teams():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.hltv.org/ranking/teams/")

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        ranking_block = soup.find("div", {"class": "ranking"})
        if not ranking_block:
            print("Ranking block não encontrado!")
            return []

        teams = []

        for team in ranking_block.find_all("div", {"class": "ranked-team standard-box"}):
            if len(teams) == 30:
                break

            name = team.find('div', class_='ranking-header').select_one('.name').text.strip()
            ranking = int(team.select_one('.position').text.strip().replace("#", ""))
            points = int(team.find('span', {'class': 'points'}).text.strip('()').split(' ')[0])

            team_url = "https://www.hltv.org" + team.find('a', {'class': 'details moreLink'})['href']

            players = []
            for player_div in team.find_all("td", {"class": "player-holder"}):
                player_link = player_div.find('a', class_='pointer')
                if not player_link:
                    continue

                player_id = int(player_link['href'].split('/')[-2])
                player_name = player_link['href'].split('/')[-1]
                player_nickname = player_link.text.strip()
                player_url = "https://www.hltv.org" + player_link['href']

                players.append({
                    'id': player_id,
                    'name': player_name,
                    'nickname': player_nickname,
                    'url': player_url
                })

            teams.append({
                'name': name,
                'ranking': ranking,
                'points': points,
                'url': team_url,
                'players': players
            })

        browser.close()
        return teams
