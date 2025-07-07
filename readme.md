# Sistema HLTV Expandido - Documentação Completa

## Visão Geral

O sistema HLTV expandido é uma API RESTful para acessar dados de times e jogadores de Counter-Strike 2, com foco em estatísticas detalhadas, conquistas e relacionamentos entre entidades.

## Modelos de Dados

### Team
- `id`: Identificador único do time (Integer)
- `name`: Nome do time (String)
- `url`: URL do time na HLTV (String)
- `ranking`: Ranking do time (Integer)
- `points`: Pontos do time (Integer)
- `logo_url`: URL do logo do time (String)
- `region`: Região do time (String)
- `win_rate`: Taxa de vitória do time (Float)
- `weeks_in_top30`: Semanas no top 30 (Integer)
- `average_player_age`: Idade média dos jogadores (Float)
- `coach_name`: Nome do treinador (String)
- `peak_ranking`: Melhor ranking alcançado (Integer)
- `time_at_peak`: Tempo no melhor ranking (String)

### Player
- `id`: Identificador único do jogador (Integer)
- `nickname`: Apelido do jogador (String)
- `real_name`: Nome real do jogador (String)
- `url`: URL do jogador na HLTV (String)
- `team_id`: ID do time ao qual o jogador pertence (Integer, ForeignKey)
- `role`: Função do jogador (e.g., 'player', 'coach') (String)

### PlayerStats
- `id`: Identificador único das estatísticas (Integer)
- `player_id`: ID do jogador ao qual as estatísticas pertencem (Integer, ForeignKey, Unique)
- `picture`: URL da imagem do jogador (String)
- `country`: País do jogador (String)
- `age`: Idade do jogador (Integer)
- `total_kills`: Total de abates (Integer)
- `total_deaths`: Total de mortes (Integer)
- `headshot_percentage`: Porcentagem de headshots (Float)
- `kd_ratio`: Proporção K/D (Float)
- `damage_per_round`: Dano por round (Float)
- `grenade_damage_per_round`: Dano de granada por round (Float)
- `maps_played`: Mapas jogados (Integer)
- `rounds_played`: Rounds jogados (Integer)
- `kills_per_round`: Abates por round (Float)
- `assists_per_round`: Assistências por round (Float)
- `deaths_per_round`: Mortes por round (Float)
- `saved_by_teammate_per_round`: Salvo por companheiro por round (Float)
- `saved_teammates_per_round`: Companheiros salvos por round (Float)
- `rating`: Rating do jogador (Float)
- `last_updated`: Última atualização (DateTime)

### PlayerAchievement
- `id`: Identificador único da conquista (Integer)
- `player_id`: ID do jogador associado (Integer, ForeignKey)
- `title`: Título da conquista (String)
- `event_name`: Nome do evento (String)
- `year`: Ano da conquista (Integer)
- `placement`: Colocação (String)
- `prize_money`: Premiação em dinheiro (String)
- `trophy_image_url`: URL da imagem do troféu (String)
- `event_tier`: Nível do evento (String, e.g., 'S-Tier', 'A-Tier')
- `mvp_award`: Indica se foi um prêmio MVP (String)

### TeamAchievement
- `id`: Identificador único da conquista (Integer)
- `team_id`: ID do time associado (Integer, ForeignKey)
- `title`: Título da conquista (String)
- `event_name`: Nome do evento (String)
- `year`: Ano da conquista (Integer)
- `placement`: Colocação (String)
- `prize_money`: Premiação em dinheiro (String)
- `trophy_image_url`: URL da imagem do troféu (String)
- `event_tier`: Nível do evento (String, e.g., 'S-Tier', 'A-Tier')

### TeamMapStats
- `id`: Identificador único das estatísticas de mapa (Integer)
- `team_id`: ID do time associado (Integer, ForeignKey)
- `map_name`: Nome do mapa (String)
- `matches_played`: Partidas jogadas (Integer)
- `matches_won`: Partidas vencidas (Integer)
- `win_rate`: Taxa de vitória no mapa (Float)
- `rounds_played`: Rounds jogados (Integer)
- `rounds_won`: Rounds vencidos (Integer)
- `round_win_rate`: Taxa de vitória de rounds (Float)
- `ct_rounds_won`: Rounds CT vencidos (Integer)
- `t_rounds_won`: Rounds TR vencidos (Integer)
- `ct_win_rate`: Taxa de vitória CT (Float)
- `t_win_rate`: Taxa de vitória TR (Float)

## Rotas da API

### Times
- `GET /teams/`: Retorna uma lista de todos os times com informações básicas e filtros de busca.
  - Parâmetros de query: `skip` (Integer, opcional, padrão 0), `limit` (Integer, opcional, padrão 20), `search` (String, opcional, busca por nome do time)
- `GET /teams/{team_id}`: Retorna informações detalhadas de um time específico, incluindo estatísticas de mapas e conquistas.
  - Parâmetros de path: `team_id` (Integer, obrigatório)
- `GET /teams/{team_id}/players`: Retorna todos os jogadores de um time específico com estatísticas completas e conquistas.
  - Parâmetros de path: `team_id` (Integer, obrigatório)
- `GET /teams/search`: Busca times por critérios específicos.
  - Parâmetros de query: `name` (String, opcional, busca parcial por nome), `ranking_min` (Integer, opcional), `ranking_max` (Integer, opcional)

### Jogadores
- `GET /players/`: Retorna uma lista de todos os jogadores com estatísticas básicas e filtros de busca.
  - Parâmetros de query: `skip` (Integer, opcional, padrão 0), `limit` (Integer, opcional, padrão 20), `search` (String, opcional, busca por nickname ou nome real)
- `GET /players/{player_id}`: Retorna informações detalhadas de um jogador específico, incluindo estatísticas e conquistas.
  - Parâmetros de path: `player_id` (Integer, obrigatório)
- `GET /players/search`: Busca jogadores por critérios específicos.
  - Parâmetros de query: `nickname` (String, opcional, busca parcial por apelido), `team_id` (Integer, opcional), `role` (String, opcional)

### Estatísticas de Jogadores
- `GET /players/{player_id}/stats`: Retorna as estatísticas detalhadas de um jogador específico.
  - Parâmetros de path: `player_id` (Integer, obrigatório)
- `GET /stats/players`: Retorna estatísticas de todos os jogadores.
  - Parâmetros de query: `skip` (Integer, opcional, padrão 0), `limit` (Integer, opcional, padrão 20)

### Conquistas (Achievements)
- `GET /teams/{team_id}/achievements`: Retorna todos os achievements de um time específico.
  - Parâmetros de path: `team_id` (Integer, obrigatório)
- `GET /players/{player_id}/achievements`: Retorna todos os achievements de um jogador específico.
  - Parâmetros de path: `player_id` (Integer, obrigatório)
- `GET /achievements/`: Retorna todos os achievements do sistema com filtros opcionais.
  - Parâmetros de query: `skip` (Integer, opcional, padrão 0), `limit` (Integer, opcional, padrão 20), `achievement_type` (String, opcional, 'team' ou 'player'), `year` (Integer, opcional), `event_tier` (String, opcional)

### Estatísticas Gerais
- `GET /stats/summary`: Retorna um resumo das estatísticas gerais do sistema (total de times, jogadores, estatísticas de jogadores e porcentagem de cobertura).

## Estrutura de Arquivos

```
/upload/
├── __init__.py
├── banco.py          # Configuração do banco de dados e modelos base
├── logger.py         # Configuração de logging
├── main.py           # Aplicação FastAPI, rotas da API e lógica de negócio
├── models.py         # Definição dos modelos de dados (SQLAlchemy) para Team, Player, PlayerStats, PlayerAchievement, TeamAchievement, TeamMapStats
├── scraper.py        # Lógica de scraping (se aplicável)
├── scraper_functions.py # Funções auxiliares de scraping (se aplicável)
├── swagger_docs.py   # Configuração para documentação customizada do Swagger UI
├── test_api.py       # Testes para as rotas da API
└── SistemaHLTV-DocumentaçãoCompleta.md # Esta documentação
```

## Como Usar

Execute o docker-composer.yml para poder instalar o container com o Postgres.

Para capturar os dados dos times, execute o arquivo `scraper.py`.

```bash
run scraper.py
```

Para rodar a aplicação, execute o arquivo `main.py` com um servidor ASGI como o Uvicorn. Certifique-se de ter as dependências instaladas (FastAPI, SQLAlchemy, Uvicorn, etc.).

```bash
uvicorn main:app --reload
```

Após iniciar o servidor, você pode acessar a documentação interativa da API em `http://127.0.0.1:5000/docs` ou `http://localhost:5000/docs` e testar as rotas diretamente do navegador ou usando ferramentas como Postman ou Insomnia.

## Melhorias Futuras

- Implementação de cache para otimização de performance.
- Expansão das funcionalidades de scraping para incluir mais dados e automatização.
- Interface de usuário para visualização dos dados e interação com a API.
- Autenticação e autorização para acesso seguro à API.
- Implementação de testes de integração e end-to-end mais abrangentes.

## Conclusão

Esta documentação fornece uma visão geral abrangente da API HLTV Expandida, seus modelos de dados, rotas disponíveis e estrutura do projeto. O sistema é projetado para ser extensível, fácil de usar e fornece acesso programático a dados detalhados de Counter-Strike 2. O objetivo é oferecer uma base robusta para análise e desenvolvimento de aplicações relacionadas ao cenário competitivo de CS2.

---

