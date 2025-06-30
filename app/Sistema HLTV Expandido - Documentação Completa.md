# Sistema HLTV Expandido - Documentação Completa

## Visão Geral

O sistema HLTV expandido é uma API RESTful para acessar dados de times e jogadores de Counter-Strike 2, com foco em estatísticas básicas e relacionamentos entre entidades.

## Modelos de Dados

### Team
- `id`: Identificador único do time (Integer)
- `name`: Nome do time (String)
- `url`: URL do time na HLTV (String)
- `ranking`: Ranking do time (Integer)
- `points`: Pontos do time (Integer)

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

## Rotas da API

### Times
- `GET /teams/`: Retorna uma lista de todos os times.
  - Parâmetros de query: `skip` (Integer, opcional, padrão 0), `limit` (Integer, opcional, padrão 20)
- `GET /teams/{team_id}/players`: Retorna uma lista de jogadores de um time específico.
  - Parâmetros de path: `team_id` (Integer, obrigatório)

### Jogadores
- `GET /players/`: Retorna uma lista de todos os jogadores.
  - Parâmetros de query: `skip` (Integer, opcional, padrão 0), `limit` (Integer, opcional, padrão 20)

### Estatísticas de Jogadores
- `GET /players/{player_id}/stats`: Retorna as estatísticas detalhadas de um jogador específico.
  - Parâmetros de path: `player_id` (Integer, obrigatório)

## Estrutura de Arquivos

```
/upload/
├── __init__.py
├── banco.py          # Configuração do banco de dados
├── logger.py         # Configuração de logging
├── main.py           # Aplicação FastAPI e rotas da API
├── models.py         # Definição dos modelos de dados (SQLAlchemy)
├── scraper.py        # Lógica de scraping (se aplicável)
├── scraper_functions.py # Funções auxiliares de scraping (se aplicável)
└── SistemaHLTVExpandido-DocumentaçãoCompleta.md # Esta documentação
```

## Como Usar

Para rodar a aplicação, execute o arquivo `main.py` com um servidor ASGI como o Uvicorn.

```bash
uvicorn main:app --reload
```

Em seguida, acesse as rotas da API através do seu navegador ou de uma ferramenta como o Postman.

## Melhorias Futuras

- Implementação de cache para otimização de performance.
- Expansão das funcionalidades de scraping para incluir mais dados.
- Interface de usuário para visualização dos dados.
- Autenticação e autorização para acesso à API.

## Conclusão

Esta documentação fornece uma visão geral da API HLTV Expandida, seus modelos de dados e rotas disponíveis. O sistema é projetado para ser extensível e fácil de usar, fornecendo acesso programático a dados de Counter-Strike 2.

