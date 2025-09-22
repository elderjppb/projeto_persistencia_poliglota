# -*- coding: utf-8 -*-
"""
Módulo para interação com o banco de dados MongoDB.

"""

from pymongo import MongoClient, GEOSPHERE
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# --- Constantes ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "geodata"
COLLECTION_NAME = "locais"

# --- Funções de Conexão ---
def conectar_mongo():
    """
    Cria e retorna uma conexão com o MongoDB.
    Lança uma exceção ConnectionFailure em caso de erro.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command('ismaster')
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return client, collection
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise ConnectionFailure(
            "Erro: Não foi possível conectar ao servidor MongoDB. "
            "Verifique se o MongoDB está em execução na porta 27017."
        ) from e

def criar_indice_geoespacial():
    client = None
    try:
        client, collection = conectar_mongo()
        index_info = collection.index_information()
        if "coordenadas_2dsphere" not in index_info:
            collection.create_index([("coordenadas", GEOSPHERE)], name="coordenadas_2dsphere")
            print("Índice geoespacial 'coordenadas_2dsphere' criado com sucesso.")
    finally:
        if client:
            client.close()

# --- Funções de Manipulação de Dados ---
def inserir_local(nome_local, cidade, latitude, longitude, descricao=""):
    """
    Insere um novo documento de local na coleção.
    """
    client = None
    try:
        client, collection = conectar_mongo()
        documento = {
            "nome_local": nome_local,
            "cidade": cidade,
            "descricao": descricao,
            "coordenadas": {
                "type": "Point",
                "coordinates": [longitude, latitude]  # Formato GeoJSON: [longitude, latitude]
            }
        }
        collection.insert_one(documento)
    finally:
        if client:
            client.close()

def buscar_locais_por_cidade(cidade):
    """Busca todos os locais de uma cidade específica."""
    client = None
    try:
        client, collection = conectar_mongo()
        locais = list(collection.find({"cidade": cidade}))
        return locais
    finally:
        if client:
            client.close()

def buscar_todos_locais():
    """Retorna todos os documentos da coleção de locais."""
    client = None
    try:
        client, collection = conectar_mongo()
        locais = list(collection.find({}))
        return locais
    finally:
        if client:
            client.close()

def contar_locais():
    """Conta o número total de locais cadastrados."""
    client = None
    try:
        client, collection = conectar_mongo()
        count = collection.count_documents({})
        return count
    finally:
        if client:
            client.close()

def buscar_locais_proximos(latitude, longitude, raio_max_metros):
    """
    Busca locais dentro de um raio a partir de um ponto central.
    """
    client = None
    try:
        client, collection = conectar_mongo()
        query = {
            "coordenadas": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": raio_max_metros
                }
            }
        }
        locais = list(collection.find(query))
        return locais
    finally:
        if client:
            client.close()

