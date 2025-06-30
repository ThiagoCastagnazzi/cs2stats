# Documentação da API - Sistema HLTV Expandido

## Visão Geral

A API do Sistema HLTV Expandido fornece acesso programático a dados detalhados sobre times e jogadores de Counter-Strike 2. Esta documentação descreve todos os endpoints disponíveis, seus parâmetros, respostas e exemplos de uso.

## URL Base

```
http://localhost:8000
```

## Documentação Interativa

A API inclui documentação interativa Swagger UI disponível em:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Autenticação

Atualmente, a API não requer autenticação. Todos os endpoints são públicos.

## Formato de Resposta

Todas as respostas são retornadas em formato JSON. Em caso de erro, a resposta incluirá um campo `detail` com a descrição do erro.

## Paginação

Muitos endpoints suportam paginação através dos seguintes parâmetros de query:

- `skip`: Número de registros a pular (padrão: 0)
- `limit`: Número máximo de registros a retornar (padrão: 20)

## Endpoints

### Home

#### GET /
Endpoint de boas-vindas da API.

**Resposta:**
```json
{
  "message": "Bem-vindo à API do Sistema HLTV Expandido"
}
```

### Times

#### GET /teams/
Retorna uma lista de todos os times.

**Parâmetros de Query:**
- `skip` (integer, opcional): Número de registros a pular (padrão: 0)
- `limit` (integer, opcional): Número máximo de registros a retornar (padrão: 20)

**Resposta de Exemplo:**
```json
[
  {
    "id": 1,
    "name": "Natus Vincere",
    "url": "https://www.hltv.org/team/4608/natus-vincere",
    "ranking": 1,
    "points": 1000
  },
  {
    "id": 2,
    "name": "FaZe Clan",
    "url": "https://www.hltv.org/team/6667/faze",
    "ranking": 2,
    "points": 950
  }
]
```

#### GET /teams/{team_id}
Retorna informações detalhadas de um time específico.

**Parâmetros de Path:**
- `team_id` (integer, obrigatório): ID do time

**Resposta de Exemplo:**
```json
{
  "id": 1,
  "name": "Natus Vincere",
  "url": "https://www.hltv.org/team/4608/natus-vincere",
  "ranking": 1,
  "points": 1000
}
```

**Códigos de Status:**
- `200`: Sucesso
- `404`: Time não encontrado

#### GET /teams/{team_id}/players
Retorna todos os jogadores de um time específico.

**Parâmetros de Path:**
- `team_id` (integer, obrigatório): ID do time

**Resposta de Exemplo:**
```json
[
  {
    "id": 1,
    "nickname": "s1mple",
    "real_name": "Oleksandr Kostyliev",
    "url": "https://www.hltv.org/player/7998/s1mple",
    "role": "player",
    "team_id": 1
  },
  {
    "id": 2,
    "nickname": "electronic",
    "real_name": "Denis Sharipov",
    "url": "https://www.hltv.org/player/8918/electronic",
    "role": "player",
    "team_id": 1
  }
]
```

#### GET /teams/search
Busca times por critérios específicos.

**Parâmetros de Query:**
- `name` (string, opcional): Busca por nome (busca parcial)
- `ranking_min` (integer, opcional): Ranking mínimo
- `ranking_max` (integer, opcional): Ranking máximo

**Exemplo de Uso:**
```
GET /teams/search?name=navi&ranking_max=5
```

### Jogadores

#### GET /players/
Retorna uma lista de todos os jogadores.

**Parâmetros de Query:**
- `skip` (integer, opcional): Número de registros a pular (padrão: 0)
- `limit` (integer, opcional): Número máximo de registros a retornar (padrão: 20)

**Resposta de Exemplo:**
```json
[
  {
    "id": 1,
    "nickname": "s1mple",
    "real_name": "Oleksandr Kostyliev",
    "url": "https://www.hltv.org/player/7998/s1mple",
    "role": "player",
    "team_id": 1,
    "team_name": "Natus Vincere"
  }
]
```

#### GET /players/{player_id}
Retorna informações detalhadas de um jogador específico.

**Parâmetros de Path:**
- `player_id` (integer, obrigatório): ID do jogador

**Resposta de Exemplo:**
```json
{
  "id": 1,
  "nickname": "s1mple",
  "real_name": "Oleksandr Kostyliev",
  "url": "https://www.hltv.org/player/7998/s1mple",
  "role": "player",
  "team_id": 1,
  "team_name": "Natus Vincere"
}
```

#### GET /players/{player_id}/stats
Retorna as estatísticas detalhadas de um jogador específico.

**Parâmetros de Path:**
- `player_id` (integer, obrigatório): ID do jogador

**Resposta de Exemplo:**
```json
{
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
```

#### GET /players/search
Busca jogadores por critérios específicos.

**Parâmetros de Query:**
- `nickname` (string, opcional): Busca por apelido (busca parcial)
- `team_id` (integer, opcional): Filtra por ID do time
- `role` (string, opcional): Filtra por função (player, coach, etc.)

**Exemplo de Uso:**
```
GET /players/search?nickname=s1mple&role=player
```

### Estatísticas

#### GET /stats/players
Retorna estatísticas de todos os jogadores.

**Parâmetros de Query:**
- `skip` (integer, opcional): Número de registros a pular (padrão: 0)
- `limit` (integer, opcional): Número máximo de registros a retornar (padrão: 20)

#### GET /stats/summary
Retorna um resumo das estatísticas gerais do sistema.

**Resposta de Exemplo:**
```json
{
  "total_teams": 50,
  "total_players": 250,
  "total_player_stats": 200,
  "coverage_percentage": 80.0
}
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `404 Not Found`: Recurso não encontrado
- `422 Unprocessable Entity`: Erro de validação nos parâmetros

## Exemplos de Uso

### Python com requests

```python
import requests

# Buscar todos os times
response = requests.get("http://localhost:8000/teams/")
teams = response.json()

# Buscar jogadores de um time específico
team_id = 1
response = requests.get(f"http://localhost:8000/teams/{team_id}/players")
players = response.json()

# Buscar estatísticas de um jogador
player_id = 1
response = requests.get(f"http://localhost:8000/players/{player_id}/stats")
stats = response.json()
```

### JavaScript com fetch

```javascript
// Buscar todos os times
fetch('http://localhost:8000/teams/')
  .then(response => response.json())
  .then(teams => console.log(teams));

// Buscar jogadores de um time específico
const teamId = 1;
fetch(`http://localhost:8000/teams/${teamId}/players`)
  .then(response => response.json())
  .then(players => console.log(players));

// Buscar estatísticas de um jogador
const playerId = 1;
fetch(`http://localhost:8000/players/${playerId}/stats`)
  .then(response => response.json())
  .then(stats => console.log(stats));
```

### cURL

```bash
# Buscar todos os times
curl -X GET "http://localhost:8000/teams/"

# Buscar jogadores de um time específico
curl -X GET "http://localhost:8000/teams/1/players"

# Buscar estatísticas de um jogador
curl -X GET "http://localhost:8000/players/1/stats"

# Buscar times com filtros
curl -X GET "http://localhost:8000/teams/search?name=navi&ranking_max=5"
```

## Modelos de Dados

### Team
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | integer | Identificador único do time |
| name | string | Nome do time |
| url | string | URL do time na HLTV |
| ranking | integer | Ranking atual do time |
| points | integer | Pontos do time no ranking |

### Player
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | integer | Identificador único do jogador |
| nickname | string | Apelido do jogador |
| real_name | string | Nome real do jogador |
| url | string | URL do jogador na HLTV |
| role | string | Função do jogador (player, coach, etc.) |
| team_id | integer | ID do time do jogador |
| team_name | string | Nome do time do jogador |

### PlayerStats
| Campo | Tipo | Descrição |
|-------|------|-----------|
| player_id | integer | ID do jogador |
| player_nickname | string | Apelido do jogador |
| picture | string | URL da foto do jogador |
| country | string | País do jogador |
| age | integer | Idade do jogador |
| total_kills | integer | Total de abates |
| total_deaths | integer | Total de mortes |
| headshot_percentage | float | Porcentagem de headshots |
| kd_ratio | float | Proporção K/D |
| damage_per_round | float | Dano por round |
| grenade_damage_per_round | float | Dano de granada por round |
| maps_played | integer | Mapas jogados |
| rounds_played | integer | Rounds jogados |
| kills_per_round | float | Abates por round |
| assists_per_round | float | Assistências por round |
| deaths_per_round | float | Mortes por round |
| saved_by_teammate_per_round | float | Salvo por companheiro por round |
| saved_teammates_per_round | float | Companheiros salvos por round |
| rating | float | Rating do jogador |
| last_updated | datetime | Última atualização |

## Limitações e Considerações

- A API atualmente não implementa rate limiting
- Não há autenticação ou autorização
- Os dados dependem da disponibilidade do sistema de scraping
- Recomenda-se implementar cache no lado do cliente para melhor performance

## Suporte

Para suporte técnico ou dúvidas sobre a API, consulte a documentação interativa em `/docs` ou entre em contato com a equipe de desenvolvimento.

