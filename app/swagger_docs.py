"""
Configuração da documentação Swagger para a API HLTV Expandido
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    """
    Configuração customizada do OpenAPI/Swagger
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Sistema HLTV Expandido API",
        version="1.0.0",
        description="""
        ## API para acessar dados de times e jogadores de Counter-Strike 2

        Esta API fornece acesso a dados detalhados sobre times e jogadores de Counter-Strike 2,
        incluindo estatísticas de desempenho, informações de times e relacionamentos entre entidades.

        ### Principais funcionalidades:

        - **Times**: Consulta de times, rankings e pontuações
        - **Jogadores**: Informações detalhadas sobre jogadores
        - **Estatísticas**: Métricas de desempenho dos jogadores
        - **Busca**: Filtros avançados para times e jogadores

        ### Modelos de dados:

        - **Team**: Informações básicas dos times
        - **Player**: Dados dos jogadores e suas funções
        - **PlayerStats**: Estatísticas detalhadas de desempenho

        ### Paginação:

        A maioria dos endpoints suporta paginação através dos parâmetros `skip` e `limit`.

        ### Códigos de resposta:

        - **200**: Sucesso
        - **404**: Recurso não encontrado
        - **422**: Erro de validação
        """,
        routes=app.routes,
        contact={
            "name": "Sistema HLTV Expandido",
            "email": "contato@hltv-expandido.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )

    # Configurações adicionais do schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://www.hltv.org/img/static/TopLogoDark2x.png"
    }

    # Tags para organização dos endpoints
    openapi_schema["tags"] = [
        {
            "name": "Home",
            "description": "Endpoint de boas-vindas"
        },
        {
            "name": "Teams",
            "description": "Operações relacionadas a times"
        },
        {
            "name": "Players",
            "description": "Operações relacionadas a jogadores"
        },
        {
            "name": "Player Stats",
            "description": "Estatísticas detalhadas dos jogadores"
        },
        {
            "name": "Stats",
            "description": "Estatísticas gerais do sistema"
        }
    ]

    # Exemplos de resposta para os modelos
    openapi_schema["components"]["examples"] = {
        "TeamExample": {
            "summary": "Exemplo de Time",
            "value": {
                "id": 1,
                "name": "Natus Vincere",
                "url": "https://www.hltv.org/team/4608/natus-vincere",
                "ranking": 1,
                "points": 1000
            }
        },
        "PlayerExample": {
            "summary": "Exemplo de Jogador",
            "value": {
                "id": 1,
                "nickname": "s1mple",
                "real_name": "Oleksandr Kostyliev",
                "url": "https://www.hltv.org/player/7998/s1mple",
                "role": "player",
                "team_id": 1,
                "team_name": "Natus Vincere"
            }
        },
        "PlayerStatsExample": {
            "summary": "Exemplo de Estatísticas",
            "value": {
                "player_id": 1,
                "player_nickname": "s1mple",
                "picture": "https://static.hltv.org/images/playerprofile/thumb/7998/400.jpeg",
                "country": "Ukraine",
                "age": 26,
                "total_kills": 15420,
                "total_deaths": 12180,
                "headshot_percentage": 52.3,
                "kd_ratio": 1.27,
                "damage_per_round": 85.4,
                "grenade_damage_per_round": 3.2,
                "maps_played": 1250,
                "rounds_played": 32500,
                "kills_per_round": 0.75,
                "assists_per_round": 0.15,
                "deaths_per_round": 0.59,
                "saved_by_teammate_per_round": 0.08,
                "saved_teammates_per_round": 0.12,
                "rating": 1.28,
                "last_updated": "2024-01-15T10:30:00"
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Schemas de resposta para documentação
team_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "description": "ID único do time"},
        "name": {"type": "string", "description": "Nome do time"},
        "url": {"type": "string", "description": "URL do time na HLTV"},
        "ranking": {"type": "integer", "description": "Ranking atual do time"},
        "points": {"type": "integer", "description": "Pontos do time no ranking"}
    },
    "required": ["id", "name"]
}

player_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "description": "ID único do jogador"},
        "nickname": {"type": "string", "description": "Apelido do jogador"},
        "real_name": {"type": "string", "description": "Nome real do jogador"},
        "url": {"type": "string", "description": "URL do jogador na HLTV"},
        "role": {"type": "string", "description": "Função do jogador (player, coach, etc.)"},
        "team_id": {"type": "integer", "description": "ID do time do jogador"},
        "team_name": {"type": "string", "description": "Nome do time do jogador"}
    },
    "required": ["id", "nickname"]
}

player_stats_response_schema = {
    "type": "object",
    "properties": {
        "player_id": {"type": "integer", "description": "ID do jogador"},
        "player_nickname": {"type": "string", "description": "Apelido do jogador"},
        "picture": {"type": "string", "description": "URL da foto do jogador"},
        "country": {"type": "string", "description": "País do jogador"},
        "age": {"type": "integer", "description": "Idade do jogador"},
        "total_kills": {"type": "integer", "description": "Total de abates"},
        "total_deaths": {"type": "integer", "description": "Total de mortes"},
        "headshot_percentage": {"type": "number", "description": "Porcentagem de headshots"},
        "kd_ratio": {"type": "number", "description": "Proporção K/D"},
        "damage_per_round": {"type": "number", "description": "Dano por round"},
        "grenade_damage_per_round": {"type": "number", "description": "Dano de granada por round"},
        "maps_played": {"type": "integer", "description": "Mapas jogados"},
        "rounds_played": {"type": "integer", "description": "Rounds jogados"},
        "kills_per_round": {"type": "number", "description": "Abates por round"},
        "assists_per_round": {"type": "number", "description": "Assistências por round"},
        "deaths_per_round": {"type": "number", "description": "Mortes por round"},
        "saved_by_teammate_per_round": {"type": "number", "description": "Salvo por companheiro por round"},
        "saved_teammates_per_round": {"type": "number", "description": "Companheiros salvos por round"},
        "rating": {"type": "number", "description": "Rating do jogador"},
        "last_updated": {"type": "string", "format": "date-time", "description": "Última atualização"}
    },
    "required": ["player_id", "player_nickname"]
}

