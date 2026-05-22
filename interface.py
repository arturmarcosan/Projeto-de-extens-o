import flet as ft
import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000"

AZUL     = "#1A73E8"
VERDE    = "#34A853"
VERMELHO = "#EA4335"
AMARELO  = "#F9AB00"
CINZA_BG = "#F8F9FA"
BRANCO   = "#FFFFFF"
TEXTO    = "#202124"
SUBTEXTO = "#5F6368"
BORDA    = "#DADCE0"


def api_post(endpoint, dados):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(dados).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        return None, json.loads(e.read()).get("detail", "Erro desconhecido")
    except Exception:
        return None, "API offline. Inicie com: uvicorn api.main:app --reload"


def api_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read()), None
    except Exception:
        return None, "API offline. Inicie com: uvicorn api.main:app --reload"


def main(page: ft.Page):
    page.title = "Bot de Lembretes de Estudos"
    page.bgcolor = CINZA_BG
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    def mostrar_msg(texto, cor=VERDE):
        page.snack_bar = ft.SnackBar(
            ft.Text(texto, color="white", weight=ft.FontWeight.W_500),
            bgcolor=cor,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()

    # ── Campos ──────────────────────────────────────────────
    nome_field = ft.TextField(
        label="Nome completo",
        border_color=BORDA,
        focused_border_color=AZUL,
        border_radius=12,
    )
    email_field = ft.TextField(
        label="E-mail",
        border_color=BORDA,
        focused_border_color=AZUL,
        border_radius=12,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    resultado_cadastro = ft.Text("", color=SUBTEXTO, size=13)

    id_estudante_field = ft.TextField(
        label="ID do Estudante",
        border_color=BORDA,
        focused_border_color=AZUL,
        border_radius=12,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    materia_field = ft.TextField(
        label="Nome da matéria",
        border_color=BORDA,
        focused_border_color=AZUL,
        border_radius=12,
    )
    dia_dropdown = ft.Dropdown(
        label="Dia da semana",
        border_color=BORDA,
        focused_border_color=AZUL,
        border_radius=12,
        options=[
            ft.dropdown.Option("segunda", "Segunda-feira"),
            ft.dropdown.Option("terca",   "Terça-feira"),
            ft.dropdown.Option("quarta",  "Quarta-feira"),
            ft.dropdown.Option("quinta",  "Quinta-feira"),
            ft.dropdown.Option("sexta",   "Sexta-feira"),
            ft.dropdown.Option("sabado",  "Sábado"),
            ft.dropdown.Option("domingo", "Domingo"),
        ],
    )
    horario_field = ft.TextField(
        label="Horário (ex: 14:00)",
        border_color=BORDA,
        focused_border_color=AZUL,
        border_radius=12,
    )

    lista_estudantes = ft.Column(spacing=8)
    lembretes_col    = ft.Column(spacing=8)

    # ── Ações ────────────────────────────────────────────────
    def cadastrar_estudante(e):
        if not nome_field.value or not email_field.value:
            mostrar_msg("Preencha nome e e-mail!", VERMELHO)
            return
        resp, erro = api_post("/estudantes", {"nome": nome_field.value, "email": email_field.value})
        if erro:
            mostrar_msg(str(erro), VERMELHO)
        else:
            resultado_cadastro.value = f"✅ Cadastrado! ID: {resp['id']} — use este ID para cadastrar matérias."
            resultado_cadastro.color = VERDE
            nome_field.value = ""
            email_field.value = ""
            mostrar_msg(f"Estudante cadastrado com ID {resp['id']}!")
            carregar_estudantes()
        page.update()

    def cadastrar_materia(e):
        if not id_estudante_field.value or not materia_field.value or not dia_dropdown.value or not horario_field.value:
            mostrar_msg("Preencha todos os campos!", VERMELHO)
            return
        dados = {
            "estudante_id": int(id_estudante_field.value),
            "nome": materia_field.value,
            "dia_semana": dia_dropdown.value,
            "horario": horario_field.value,
        }
        resp, erro = api_post("/materias", dados)
        if erro:
            mostrar_msg(str(erro), VERMELHO)
        else:
            materia_field.value = ""
            horario_field.value = ""
            dia_dropdown.value = None
            mostrar_msg("Matéria cadastrada com sucesso!")
        page.update()

    def carregar_estudantes(e=None):
        resp, erro = api_get("/estudantes")
        lista_estudantes.controls.clear()
        if erro:
            lista_estudantes.controls.append(ft.Text(erro, color=VERMELHO, size=13))
        elif not resp:
            lista_estudantes.controls.append(ft.Text("Nenhum estudante cadastrado.", color=SUBTEXTO, size=13))
        else:
            for est in resp:
                lista_estudantes.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(est["nome"][0].upper(), color="white", weight=ft.FontWeight.BOLD, size=16),
                                width=40, height=40,
                                bgcolor=AZUL,
                                border_radius=20,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column([
                                ft.Text(est["nome"], weight=ft.FontWeight.W_600, color=TEXTO, size=14),
                                ft.Text(est["email"], color=SUBTEXTO, size=12),
                            ], spacing=2, expand=True),
                            ft.Text(f"ID: {est['id']}", color=AZUL, size=12, weight=ft.FontWeight.W_600),
                        ], spacing=12),
                        padding=14,
                        bgcolor=BRANCO,
                        border_radius=12,
                        border=ft.border.all(1, BORDA),
                    )
                )
        page.update()

    def ver_lembretes(e):
        resp, erro = api_get("/lembretes/agora")
        lembretes_col.controls.clear()
        if erro:
            lembretes_col.controls.append(ft.Text(erro, color=VERMELHO, size=13))
        else:
            lembretes_col.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"📅 {resp['dia'].capitalize()}  🕐 {resp['hora']}  —  {resp['total']} lembrete(s)",
                        color=AZUL, size=13, weight=ft.FontWeight.W_600
                    ),
                    padding=12,
                    bgcolor="#E8F0FE",
                    border_radius=10,
                )
            )
            if resp["total"] == 0:
                lembretes_col.controls.append(ft.Text("Nenhuma aula no horário atual.", color=SUBTEXTO, size=13))
            else:
                for l in resp["lembretes"]:
                    lembretes_col.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(l["materia"], weight=ft.FontWeight.W_600, color=TEXTO, size=14),
                                ft.Text(l["estudante_nome"], color=SUBTEXTO, size=12),
                                ft.Text(f"📧 {l['estudante_email']}", color=SUBTEXTO, size=12),
                            ], spacing=4),
                            padding=14,
                            bgcolor=BRANCO,
                            border_radius=12,
                            border=ft.border.all(1, BORDA),
                        )
                    )
        page.update()

    # ── Helper: card ────────────────────────────────────────
    def card(titulo, cor, conteudo):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(titulo, weight=ft.FontWeight.BOLD, color=BRANCO, size=15),
                    padding=16,
                    bgcolor=cor,
                    border_radius=ft.border_radius.only(top_left=14, top_right=14),
                ),
                ft.Container(
                    content=conteudo,
                    padding=16,
                ),
            ], spacing=0),
            bgcolor=BRANCO,
            border_radius=14,
            border=ft.border.all(1, BORDA),
        )

    def botao(texto, cor, acao):
        return ft.ElevatedButton(
            text=texto,
            on_click=acao,
            style=ft.ButtonStyle(
                bgcolor=cor,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            width=220,
            height=44,
        )

    # ── Carregar dados iniciais ──────────────────────────────
    carregar_estudantes()

    # ── Layout ──────────────────────────────────────────────
    page.add(
        ft.Column([
            # Header
            ft.Container(
                content=ft.Column([
                    ft.Text("📚 Bot de Lembretes", color="white", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("de Estudos", color="#FFFFFFBB", size=14),
                ], spacing=2),
                padding=24,
                bgcolor=AZUL,
            ),

            # Cards
            ft.Container(
                content=ft.Column([

                    card("👤 Cadastrar Estudante", AZUL, ft.Column([
                        nome_field,
                        email_field,
                        resultado_cadastro,
                        botao("Cadastrar", AZUL, cadastrar_estudante),
                    ], spacing=12)),

                    card("📘 Cadastrar Matéria", AMARELO, ft.Column([
                        id_estudante_field,
                        materia_field,
                        dia_dropdown,
                        horario_field,
                        botao("Cadastrar Matéria", AMARELO, cadastrar_materia),
                    ], spacing=12)),

                    card("👥 Estudantes Cadastrados", VERDE, ft.Column([
                        lista_estudantes,
                        ft.TextButton("🔄 Atualizar lista", on_click=carregar_estudantes),
                    ], spacing=8)),

                    card("🔔 Lembretes Agora", VERMELHO, ft.Column([
                        ft.Text("Veja quem tem aula no horário atual.", color=SUBTEXTO, size=13),
                        lembretes_col,
                        botao("Verificar agora", VERMELHO, ver_lembretes),
                    ], spacing=12)),

                ], spacing=16),
                padding=16,
            ),
        ], spacing=0)
    )


ft.app(target=main)
