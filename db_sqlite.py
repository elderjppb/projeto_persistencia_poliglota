# -*- coding: utf-8 -*-
"""
Módulo para interação com o banco de dados SQLite.

"""

import sqlite3

# --- Constantes ---
DB_NAME = "dados_relacionais.db"


# --- Funções de Conexão ---
def conectar_bd():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    return conn


# --- Funções de Estrutura (DDL) ---
def criar_tabelas():
    """Cria as tabelas do banco de dados se elas não existirem."""
    conn = conectar_bd()
    cursor = conn.cursor()

    # Tabela de Países
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # Tabela de Estados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        sigla TEXT NOT NULL UNIQUE,
        id_pais INTEGER,
        FOREIGN KEY (id_pais) REFERENCES paises(id)
    )
    """)

    # Tabela de Cidades
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        id_estado INTEGER,
        FOREIGN KEY (id_estado) REFERENCES estados(id)
    )
    """)

    conn.commit()
    conn.close()


# --- Funções de Manipulação de Dados ---

# PAÍSES
def inserir_pais(nome):
    """Insere um novo país na tabela 'paises'."""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO paises (nome) VALUES (?)", (nome,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"País '{nome}' já existe.")
    finally:
        conn.close()


def listar_paises():
    """Retorna uma lista de todos os países."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paises")
    paises = cursor.fetchall()
    conn.close()
    return paises


# ESTADOS
def inserir_estado(nome, sigla, id_pais):
    """Insere um novo estado na tabela 'estados'."""
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO estados (nome, sigla, id_pais) VALUES (?, ?, ?)", (nome, sigla, id_pais))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Estado com sigla '{sigla}' já existe.")
    finally:
        conn.close()


def listar_estados():
    """Retorna uma lista de todos os estados."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estados")
    estados = cursor.fetchall()
    conn.close()
    return estados


# CIDADES
def inserir_cidade(nome, id_estado):
    """Insere uma nova cidade na tabela 'cidades'."""
    conn = conectar_bd()
    cursor = conn.cursor()
    # Verifica se a combinação cidade/estado já existe para evitar duplicatas
    cursor.execute("SELECT id FROM cidades WHERE nome = ? AND id_estado = ?", (nome, id_estado))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO cidades (nome, id_estado) VALUES (?, ?)", (nome, id_estado))
        conn.commit()
    else:
        print(f"Cidade '{nome}' no estado ID {id_estado} já existe.")
    conn.close()


def listar_cidades():
    """Retorna uma lista de todas as cidades."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT c.id, c.nome, e.sigla FROM cidades c JOIN estados e ON c.id_estado = e.id ORDER BY c.nome")
    cidades = cursor.fetchall()
    conn.close()
    return cidades


# --- Execução Inicial ---
if __name__ == '__main__':

    print("Inicializando banco de dados SQLite...")
    criar_tabelas()

    # Populando com dados de exemplo
    if not listar_paises():
        inserir_pais("Brasil")
        print("País 'Brasil' inserido.")

    id_brasil = listar_paises()[0][0]

    if not listar_estados():
        inserir_estado("Paraíba", "PB", id_brasil)
        inserir_estado("Pernambuco", "PE", id_brasil)
        print("Estados 'Paraíba' e 'Pernambuco' inseridos.")

    estados = {e[2]: e[0] for e in listar_estados()}  # sigla -> id

    if not listar_cidades():
        inserir_cidade("João Pessoa", estados['PB'])
        inserir_cidade("Campina Grande", estados['PB'])
        inserir_cidade("Recife", estados['PE'])
        print("Cidades de exemplo inseridas.")

    print("Banco de dados pronto.")
    print("\nCidades cadastradas:")
    for cidade in listar_cidades():
        print(f"- {cidade[1]} ({cidade[2]})")
