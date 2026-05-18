"""
demo.py — Script de demonstração
Popula o banco com dados de exemplo chamando a própria API.

Como usar:
    1. Certifique-se que a API está rodando: uvicorn api.main:app --reload
    2. Em outro terminal: python demo.py
"""

import urllib.request
import urllib.error
import json


BASE_URL = "http://localhost:8000"


def post(endpoint, dados):
    """Faz uma requisição POST e retorna a resposta como dicionário."""
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(dados).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def get(endpoint):
    """Faz uma requisição GET e retorna a resposta como dicionário."""
    url = f"{BASE_URL}{endpoint}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def separador(titulo):
    print(f"\n{'─'*45}")
    print(f"  {titulo}")
    print(f"{'─'*45}")


# ──────────────────────────────────────────
separador("1. Cadastrando estudantes")
# ──────────────────────────────────────────

estudante1 = post("/estudantes", {"nome": "Ana Silva", "email": "ana@email.com"})
print(f"✅ {estudante1}")

estudante2 = post("/estudantes", {"nome": "Bruno Costa", "email": "bruno@email.com"})
print(f"✅ {estudante2}")

id_ana = estudante1.get("id")
id_bruno = estudante2.get("id")


# ──────────────────────────────────────────
separador("2. Cadastrando matérias")
# ──────────────────────────────────────────

materias = [
    {"estudante_id": id_ana,   "nome": "Cálculo",      "dia_semana": "segunda", "horario": "08:00"},
    {"estudante_id": id_ana,   "nome": "Física",        "dia_semana": "quarta",  "horario": "10:00"},
    {"estudante_id": id_bruno, "nome": "Programação",   "dia_semana": "terca",   "horario": "14:00"},
    {"estudante_id": id_bruno, "nome": "Banco de Dados","dia_semana": "quinta",  "horario": "16:00"},
]

for m in materias:
    resp = post("/materias", m)
    print(f"✅ {m['nome']} ({m['dia_semana']} às {m['horario']}) → {resp}")


# ──────────────────────────────────────────
separador("3. Listando tudo cadastrado")
# ──────────────────────────────────────────

estudantes = get("/estudantes")
print(f"\nEstudantes cadastrados: {len(estudantes)}")
for e in estudantes:
    print(f"  • [{e['id']}] {e['nome']} — {e['email']}")

    materias_do_estudante = get(f"/materias/{e['id']}")
    for m in materias_do_estudante:
        print(f"      📘 {m['nome']} — {m['dia_semana']} às {m['horario']}")


# ──────────────────────────────────────────
separador("4. Simulando o n8n (lembretes agora)")
# ──────────────────────────────────────────

resultado = get("/lembretes/agora")
print(f"\nHoje é {resultado['dia']} às {resultado['hora']}")
print(f"Lembretes encontrados: {resultado['total']}")

if resultado["total"] > 0:
    for lembrete in resultado["lembretes"]:
        print(f"  📧 E-mail para {lembrete['estudante_email']}: aula de {lembrete['materia']} às {lembrete['horario']}")
else:
    print("  (Nenhuma aula no horário atual — tente alterar um horário no banco para o horário de agora)")

print("\n✅ Demo concluída! Acesse http://localhost:8000/docs para explorar a API.")
