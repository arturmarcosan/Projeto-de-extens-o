import sqlite3

# Nome do arquivo do banco de dados
DB_NAME = "estudos.db"


def get_connection():
    """
    Retorna uma conexão com o banco de dados.
    O 'check_same_thread=False' é necessário para funcionar com o FastAPI.
    """
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn


def criar_tabelas():
    """
    Cria as tabelas do banco se ainda não existirem.
    Chamada uma vez quando a API inicia.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de estudantes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudantes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            email     TEXT    NOT NULL UNIQUE
        )
    """)

    # Tabela de matérias vinculadas a um estudante
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            estudante_id  INTEGER NOT NULL,
            nome          TEXT    NOT NULL,
            dia_semana    TEXT    NOT NULL,  -- ex: 'segunda', 'terca'
            horario       TEXT    NOT NULL,  -- ex: '14:00'
            FOREIGN KEY (estudante_id) REFERENCES estudantes(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Banco de dados pronto.")
