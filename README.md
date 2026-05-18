# 📚 Bot de Lembretes de Estudos

Projeto de extensão universitária que ajuda estudantes a organizarem seus horários de estudo com lembretes automáticos via e-mail.

## 🛠️ Tecnologias
- **Python + FastAPI** — API REST para gerenciar matérias e horários
- **SQLite** — Banco de dados local, sem necessidade de instalação extra
- **n8n** — Agente de automação que dispara os lembretes nos horários certos
- **Git/GitHub** — Versionamento do código

## 🚀 Como rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/projeto-extensao.git
cd projeto-extensao
```

### 2. Crie o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Inicie a API
```bash
uvicorn api.main:app --reload
```

### 5. Acesse a documentação interativa
```
http://localhost:8000/docs
```

## 📁 Estrutura do Projeto
```
projeto-extensao/
├── api/
│   ├── main.py          # Endpoints da API
│   └── database.py      # Conexão e criação do banco
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔄 Fluxo do Sistema
1. Estudante cadastra matérias e horários via API
2. n8n verifica a cada hora quais matérias estão no horário atual
3. n8n envia e-mail de lembrete para o estudante
