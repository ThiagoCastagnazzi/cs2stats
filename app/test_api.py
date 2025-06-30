#!/usr/bin/env python3
"""
Script de teste para a API HLTV Expandido
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Testa se todas as importações funcionam"""
    print("=== Teste de Importações ===")

    try:
        from main import app
        print("✓ Importação da aplicação principal bem-sucedida")
    except Exception as e:
        print(f"✗ Erro na importação da aplicação: {e}")
        return False

    try:
        from swagger_docs import custom_openapi
        print("✓ Configuração do Swagger importada com sucesso")
    except Exception as e:
        print(f"✗ Erro na importação do Swagger: {e}")
        return False

    try:
        from app import models
        print("✓ Modelos importados com sucesso")
    except Exception as e:
        print(f"✗ Erro na importação dos modelos: {e}")
        return False

    return True


def test_app_configuration():
    """Testa a configuração da aplicação"""
    print("\n=== Teste de Configuração da Aplicação ===")

    try:
        from main import app

        # Verifica se a aplicação foi criada
        assert app is not None, "Aplicação não foi criada"
        print("✓ Aplicação criada com sucesso")

        # Verifica configurações básicas
        assert app.title == "Sistema HLTV Expandido API", "Título incorreto"
        print("✓ Título da aplicação correto")

        assert app.version == "1.0.0", "Versão incorreta"
        print("✓ Versão da aplicação correta")

        return True

    except Exception as e:
        print(f"✗ Erro na configuração da aplicação: {e}")
        return False


def test_routes():
    """Testa se as rotas foram definidas corretamente"""
    print("\n=== Teste de Rotas ===")

    try:
        from main import app

        # Lista de rotas esperadas
        expected_routes = [
            "/",
            "/teams/",
            "/teams/{team_id}",
            "/teams/{team_id}/players",
            "/teams/search",
            "/players/",
            "/players/{player_id}",
            "/players/{player_id}/stats",
            "/players/search",
            "/stats/players",
            "/stats/summary"
        ]

        # Obter rotas da aplicação
        app_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                app_routes.append(route.path)

        # Verificar se todas as rotas esperadas existem
        missing_routes = []
        for expected_route in expected_routes:
            if expected_route not in app_routes:
                missing_routes.append(expected_route)

        if missing_routes:
            print(f"✗ Rotas faltando: {missing_routes}")
            return False
        else:
            print(f"✓ Todas as {len(expected_routes)} rotas esperadas foram encontradas")
            return True

    except Exception as e:
        print(f"✗ Erro ao verificar rotas: {e}")
        return False


def test_swagger_configuration():
    """Testa a configuração do Swagger"""
    print("\n=== Teste de Configuração do Swagger ===")

    try:
        from main import app
        from swagger_docs import custom_openapi

        # Testa se a função de OpenAPI customizada funciona
        openapi_schema = custom_openapi(app)

        assert openapi_schema is not None, "Schema OpenAPI não foi gerado"
        print("✓ Schema OpenAPI gerado com sucesso")

        assert "info" in openapi_schema, "Informações básicas não encontradas no schema"
        print("✓ Informações básicas presentes no schema")

        assert "tags" in openapi_schema, "Tags não encontradas no schema"
        print("✓ Tags de organização presentes no schema")

        return True

    except Exception as e:
        print(f"✗ Erro na configuração do Swagger: {e}")
        return False


def test_models():
    """Testa os modelos de dados"""
    print("\n=== Teste de Modelos ===")

    try:
        from app import models

        # Verifica se as classes existem
        assert hasattr(models, 'Team'), "Modelo Team não encontrado"
        print("✓ Modelo Team encontrado")

        assert hasattr(models, 'Player'), "Modelo Player não encontrado"
        print("✓ Modelo Player encontrado")

        assert hasattr(models, 'PlayerStats'), "Modelo PlayerStats não encontrado"
        print("✓ Modelo PlayerStats encontrado")

        # Verifica se as classes têm os atributos esperados
        team_attrs = ['id', 'name', 'url', 'ranking', 'points']
        for attr in team_attrs:
            assert hasattr(models.Team, attr), f"Atributo {attr} não encontrado em Team"
        print("✓ Atributos do modelo Team verificados")

        player_attrs = ['id', 'nickname', 'real_name', 'url', 'team_id', 'role']
        for attr in player_attrs:
            assert hasattr(models.Player, attr), f"Atributo {attr} não encontrado em Player"
        print("✓ Atributos do modelo Player verificados")

        stats_attrs = ['id', 'player_id', 'total_kills', 'total_deaths', 'kd_ratio', 'rating']
        for attr in stats_attrs:
            assert hasattr(models.PlayerStats, attr), f"Atributo {attr} não encontrado em PlayerStats"
        print("✓ Atributos do modelo PlayerStats verificados")

        return True

    except Exception as e:
        print(f"✗ Erro nos modelos: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("Iniciando testes da API HLTV Expandido...\n")

    tests = [
        test_imports,
        test_app_configuration,
        test_routes,
        test_swagger_configuration,
        test_models
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=== Resumo dos Testes ===")
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Testes falharam: {total - passed}")

    if passed == total:
        print("✓ Todos os testes passaram! A API está funcionando corretamente.")
        return True
    else:
        print("✗ Alguns testes falharam. Verifique os erros acima.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
