# DocMind

O DocMind é um assistente de pesquisa documental. Ele transforma PDFs e arquivos TXT em conteúdo pesquisável para ajudar a encontrar informações e responder perguntas sem precisar percorrer o documento inteiro.

## IA e busca

O projeto usa um fluxo de RAG: extrai o texto, encontra os trechos mais relacionados à pergunta e envia esses trechos ao modelo de IA para gerar uma resposta com referências. Assim, é possível conferir a resposta no documento original.

Com `GROQ_API_KEY`, o Groq gera respostas usando trechos encontrados pela busca textual. Com `OPENAI_API_KEY` e sem chave Groq, o sistema também cria embeddings para combinar busca por palavras e por significado. Sem nenhuma chave, a busca textual continua disponível, mas não há respostas geradas por IA.

## Como funciona

1. O sistema extrai o texto e o salva em trechos no PostgreSQL.
2. A busca seleciona trechos relevantes para a pergunta.
3. Quando há um provedor de IA configurado, o modelo responde com base nesses trechos e inclui referências.

## Rodar localmente

Você precisa de Python 3.11+, Node.js 20+, npm e Docker Compose.

Na pasta `docmind-python`, prepare o ambiente uma vez.

**Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
npm --prefix frontend install
```

**Linux ou macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
npm --prefix frontend install
```

No `.env`, preencha a chave do provedor que você escolheu. As demais configurações já apontam para o PostgreSQL local.

Inicie o banco e, em seguida, a aplicação:

```bash
docker compose up -d --wait
```

```powershell
# Windows
npm run dev
```

```bash
# Linux ou macOS
npm run dev:unix
```

Abra <http://127.0.0.1:5173>. A API fica em <http://127.0.0.1:8084/api/docs>. `Ctrl+C` encerra a aplicação.

## Testes

```bash
python -m pytest -q
```

## Limites

Aceita arquivos de até 8 MB e PDFs com texto selecionável; ainda não há OCR para PDFs escaneados. Com a IA habilitada, os trechos encontrados são enviados ao provedor configurado. O projeto não tem autenticação e é voltado a uso local.
