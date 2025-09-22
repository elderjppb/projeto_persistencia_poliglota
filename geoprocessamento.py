# -*- coding: utf-8 -*-
"""
Módulo para funções de geoprocessamento.

"""

from geopy.distance import geodesic
import db_mongo


def calcular_distancia_km(ponto1, ponto2):

    if not ponto1 or not ponto2:
        return 0.0
    return geodesic(ponto1, ponto2).kilometers


def encontrar_locais_proximos(latitude, longitude, raio_max_metros):

    locais = db_mongo.buscar_locais_proximos(latitude, longitude, raio_max_metros)
    return locais


# --- Exemplo de Uso ---
if __name__ == '__main__':
    # Coordenadas de exemplo: João Pessoa e Recife
    jp_coords = (-7.1197, -34.8785)
    recife_coords = (-8.0577, -34.8829)

    distancia = calcular_distancia_km(jp_coords, recife_coords)
    print(f"A distância entre João Pessoa e Recife é de aproximadamente {distancia:.2f} km.")

    # Exemplo de busca por proximidade (usando dados de teste do MongoDB)
    print("\nBuscando locais próximos ao centro de João Pessoa (raio de 5km)...")
    # Para este teste funcionar, garanta que há dados no MongoDB.
    # Rode `app.py` primeiro para popular o banco.
    locais = encontrar_locais_proximos(
        latitude=jp_coords[0],
        longitude=jp_coords[1],
        raio_max_metros=5000
    )

    if locais:
        print(f"Encontrados {len(locais)} locais:")
        for local in locais:
            print(f"- {local['nome_local']} em {local['cidade']}")
    else:
        print("Nenhum local encontrado. Popule o banco de dados executando app.py.")
