# Sistema HLTV Expandido

API RESTful para acessar dados de times e jogadores de Counter-Strike 2, com documentação Swagger integrada.

## Características

- **API RESTful completa** com endpoints para times, jogadores e estatísticas
- **Documentação Swagger/OpenAPI** interativa
- **Modelos de dados robustos** com relacionamentos
- **Busca e filtros avançados**
- **Paginação** em todos os endpoints de listagem
- **Suporte a SQLite e PostgreSQL**

## Estrutura do Projeto

```
/
├── app/
│   ├── __init__.py          # Inicialização do módulo
│   ├── banco.py             # Configuração do banco de dados
│   ├── logger.py            # Configuração de logging
│   └── models.py            # Modelos SQLAlchemy
├── main.py                  # Aplicação FastAPI principal
├── swagger_docs.py          # Configuração do Swagger
├── test_api.py              # Testes automatizados
├── API_Documentation.md     # Documentação detalhada da API
├── SistemaHLTVExpandido-DocumentaçãoCompleta.md  # Documentação do sistema
└── README.md                # Este arquivo
```

## Instalação

1. **Instalar dependências:**
```bash
pip install fastapi[all] uvicorn sqlalchemy
```

2. **Configurar banco de dados:**
   - Por padrão, usa SQLite (`cs2stats.db`)
   - Para PostgreSQL, defina a variável `DATABASE_URL`

3. **Executar a aplicação:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints Principais

### Times
- `GET /teams/` - Lista todos os times
- `GET /teams/{team_id}` - Detalhes de um time
- `GET /teams/{team_id}/players` - Jogadores de um time
- `GET /teams/search` - Busca times por critérios

### Jogadores
- `GET /players/` - Lista todos os jogadores
- `GET /players/{player_id}` - Detalhes de um jogador
- `GET /players/{player_id}/stats` - Estatísticas de um jogador
- `GET /players/search` - Busca jogadores por critérios

### Estatísticas
- `GET /stats/players` - Estatísticas de todos os jogadores
- `GET /stats/summary` - Resumo geral do sistema

## Modelos de Dados

### Team
- `id`: ID único do time
- `name`: Nome do time
- `url`: URL na HLTV
- `ranking`: Posição no ranking
- `points`: Pontos no ranking

### Player
- `id`: ID único do jogador
- `nickname`: Apelido do jogador
- `real_name`: Nome real
- `url`: URL na HLTV
- `team_id`: ID do time
- `role`: Função (player, coach, etc.)

### PlayerStats
- `player_id`: ID do jogador
- `total_kills`: Total de abates
- `total_deaths`: Total de mortes
- `kd_ratio`: Proporção K/D
- `rating`: Rating do jogador
- `damage_per_round`: Dano por round
- E muitas outras métricas...

## Exemplos de Uso

### Python
```python
import requests

# Buscar todos os times
response = requests.get("http://localhost:8000/teams/")
teams = response.json()

# Buscar jogadores de um time
response = requests.get("http://localhost:8000/teams/1/players")
players = response.json()

# Buscar estatísticas de um jogador
response = requests.get("http://localhost:8000/players/1/stats")
stats = response.json()
```

### JavaScript
```javascript
// Buscar times
fetch('http://localhost:8000/teams/')
  .then(response => response.json())
  .then(teams => console.log(teams));

// Buscar com filtros
fetch('http://localhost:8000/teams/search?name=navi&ranking_max=5')
  .then(response => response.json())
  .then(teams => console.log(teams));
```

### cURL
```bash
# Buscar todos os times
curl -X GET "http://localhost:8000/teams/"

# Buscar com paginação
curl -X GET "http://localhost:8000/teams/?skip=0&limit=10"

# Buscar estatísticas
curl -X GET "http://localhost:8000/players/1/stats"
```

## Testes

Execute os testes automatizados:

```bash
python test_api.py
```

Os testes verificam:
- Importações e configurações
- Definição de rotas
- Configuração do Swagger
- Estrutura dos modelos

## Configuração do Banco

### SQLite (Padrão)
```python
DATABASE_URL = "sqlite:///./cs2stats.db"
```

### PostgreSQL
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/cs2stats"
```

## Recursos Avançados

### Paginação
Todos os endpoints de listagem suportam:
- `skip`: Registros a pular
- `limit`: Máximo de registros

### Busca e Filtros
- Busca por nome (parcial)
- Filtros por time, função, ranking
- Combinação de múltiplos critérios

### Documentação Interativa
- Interface Swagger completa
- Exemplos de requisição/resposta
- Teste direto dos endpoints
- Schemas detalhados

## Desenvolvimento

### Estrutura Modular
- Separação clara entre modelos, rotas e configurações
- Documentação automática via decoradores
- Configuração flexível de banco de dados

### Boas Práticas
- Validação automática via Pydantic
- Tratamento de erros consistente
- Códigos de status HTTP apropriados
- Documentação abrangente

## Próximos Passos

- [ ] Implementar autenticação
- [ ] Adicionar rate limiting
- [ ] Cache de respostas
- [ ] Métricas de performance
- [ ] Deploy em produção
- [ ] Integração com scraping automático

## Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `/docs`
2. Verifique os exemplos em `API_Documentation.md`
3. Execute os testes com `python test_api.py`

## Licença

MIT License - veja o arquivo LICENSE para detalhes.

