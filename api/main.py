from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from api.database import get_connection, criar_tabelas
from datetime import datetime

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="📚 Bot de Lembretes de Estudos",
    description="API para cadastrar estudantes, matérias e consultar lembretes do dia.",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ─────────────────────────────────────────
# MODELOS (formato dos dados que a API recebe)
# ─────────────────────────────────────────

class EstudanteEntrada(BaseModel):
    nome: str
    email: str

class MateriaEntrada(BaseModel):
    estudante_id: int
    nome: str
    dia_semana: str   # ex: 'segunda', 'terca', 'quarta'...
    horario: str      # ex: '14:00'


# ─────────────────────────────────────────
# EVENTO DE INICIALIZAÇÃO
# ─────────────────────────────────────────

@app.on_event("startup")
def startup():
    """Cria as tabelas do banco ao iniciar a API."""
    criar_tabelas()


# ─────────────────────────────────────────
# ROTA RAIZ — só para confirmar que a API está viva
# ─────────────────────────────────────────

@app.get("/")
def raiz():
    return FileResponse("static/index.html")

# ─────────────────────────────────────────
# ESTUDANTES
# ─────────────────────────────────────────

@app.post("/estudantes", summary="Cadastrar um estudante")
def cadastrar_estudante(dados: EstudanteEntrada):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO estudantes (nome, email) VALUES (?, ?)",
            (dados.nome, dados.email)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return {"mensagem": "Estudante cadastrado!", "id": novo_id}
    except Exception:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    finally:
        conn.close()


@app.get("/estudantes", summary="Listar todos os estudantes")
def listar_estudantes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estudantes")
    estudantes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return estudantes


@app.delete("/estudantes/{estudante_id}", summary="Remover um estudante")
def remover_estudante(estudante_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materias WHERE estudante_id = ?", (estudante_id,))
    cursor.execute("DELETE FROM estudantes WHERE id = ?", (estudante_id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Estudante e suas matérias removidos."}


# ─────────────────────────────────────────
# MATÉRIAS
# ─────────────────────────────────────────

@app.post("/materias", summary="Cadastrar uma matéria com horário")
def cadastrar_materia(dados: MateriaEntrada):
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se o estudante existe
    cursor.execute("SELECT id FROM estudantes WHERE id = ?", (dados.estudante_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Estudante não encontrado.")

    cursor.execute(
        "INSERT INTO materias (estudante_id, nome, dia_semana, horario) VALUES (?, ?, ?, ?)",
        (dados.estudante_id, dados.nome, dados.dia_semana.lower(), dados.horario)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return {"mensagem": "Matéria cadastrada!", "id": novo_id}


@app.get("/materias/{estudante_id}", summary="Listar matérias de um estudante")
def listar_materias(estudante_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materias WHERE estudante_id = ?", (estudante_id,))
    materias = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return materias


@app.delete("/materias/{materia_id}", summary="Remover uma matéria")
def remover_materia(materia_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materias WHERE id = ?", (materia_id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Matéria removida."}


# ─────────────────────────────────────────
# ROTA ESPECIAL — usada pelo n8n
# ─────────────────────────────────────────

@app.get("/lembretes/agora", summary="Matérias no horário atual (usada pelo n8n)")
def lembretes_agora():
    """
    Retorna todas as matérias cujo dia e horário batem com o momento atual.
    O n8n chama essa rota a cada hora e dispara e-mails para os estudantes encontrados.
    """
    agora = datetime.now()

    dias = {
        0: "segunda",
        1: "terca",
        2: "quarta",
        3: "quinta",
        4: "sexta",
        5: "sabado",
        6: "domingo"
    }

    dia_atual = dias[agora.weekday()]
    hora_atual = agora.strftime("%H:00")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            e.nome   AS estudante_nome,
            e.email  AS estudante_email,
            m.nome   AS materia,
            m.horario
        FROM materias m
        JOIN estudantes e ON e.id = m.estudante_id
        WHERE m.dia_semana = ? AND m.horario = ?
    """, (dia_atual, hora_atual))

    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "dia": dia_atual,
        "hora": hora_atual,
        "total": len(resultados),
        "lembretes": resultados
    }
