# ⚙️ Como configurar o n8n

## 1. Instalar e iniciar o n8n

```bash
# Instalar globalmente (precisa ter Node.js)
npm install -g n8n

# Iniciar o n8n
n8n start
```

Acesse: http://localhost:5678

---

## 2. Importar o workflow

1. No n8n, clique em **"New Workflow"**
2. Clique nos **três pontos** (menu) no canto superior direito
3. Selecione **"Import from file"**
4. Escolha o arquivo `workflow_lembretes.json` desta pasta
5. O workflow será carregado com todos os nós configurados

---

## 3. Configurar o nó de e-mail (Gmail)

1. Clique duas vezes no nó **"📧 Enviar e-mail"**
2. Em **Credentials**, clique em **"Create new"**
3. Siga as instruções do n8n para conectar sua conta Google
4. Substitua `seuprojeto@gmail.com` pelo seu e-mail no campo **From**

---

## 4. Fluxo do Workflow

```
⏰ A cada hora
    ↓
🔍 Chama GET /lembretes/agora na API Python
    ↓
🔀 Verifica se há lembretes (total > 0)
    ↓ (sim)
📋 Separa cada lembrete em um item individual
    ↓
📧 Envia e-mail para cada estudante com sua matéria
```

---

## 5. Ativar o workflow

Clique no toggle **"Active"** no canto superior direito do n8n.
A partir daí, o workflow roda sozinho a cada hora!

---

## Dica: Testar manualmente

Para testar sem esperar a hora cheia:
1. Clique em **"Execute Workflow"** no n8n
2. Ou acesse diretamente: `http://localhost:8000/lembretes/agora`
   e veja o que seria enviado agora
