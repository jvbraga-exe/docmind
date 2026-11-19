# DocMind

Faça perguntas sobre seus documentos e receba respostas com referências exatas às páginas originais.

Você sobe um PDF ou TXT, digita sua dúvida em português, e o DocMind busca as partes relevantes do arquivo e pede para a IA montar uma resposta baseada só no que está escrito ali — sem inventar nada.

---

## Como o projeto funciona por dentro

O DocMind tem três etapas principais:

**1. Indexação do documento**
Quando você envia um arquivo, o sistema divide o texto em pedaços menores (chamados *chunks*) e salva cada um no banco de dados. Se você usa OpenAI, também gera uma representação matemática do significado de cada pedaço — isso permite buscar por contexto e não só por palavras exatas.

**2. Busca**
Quando você faz uma pergunta, o sistema procura os pedaços mais relevantes do documento. Isso pode funcionar de dois jeitos dependendo do seu provedor de IA:

| Provedor | Como busca | Ponto forte |
|---|---|---|
| **Groq** | Busca por palavras e termos no texto | Gratuito, muito rápido, funciona bem para a maioria dos casos |
| **OpenAI** | Busca por significado + palavras | Encontra respostas mesmo quando o usuário usa palavras diferentes das do documento |

**3. Resposta**
Os pedaços encontrados vão para a IA junto com a pergunta. A IA lê o contexto e escreve uma resposta em linguagem natural, citando de onde veio cada informação.

---

## Tecnologias usadas

- **FastAPI** — backend Python assíncrono
- **LangChain** — divide os documentos e conecta com os modelos de IA
- **PostgreSQL** — salva os documentos, os pedaços e (com OpenAI) os vetores de significado
- **React + TypeScript** — interface web

---

## Como rodar localmente

### O que você precisa ter instalado

- Python 3.11 ou mais recente
- Node.js 20 ou mais recente
- Docker (para subir o banco de dados)

### 1. Instalar dependências

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

### 2. Configurar a chave de IA

Abra o arquivo `.env` e coloque a chave do provedor que você quer usar:

```env
# Opção 1: Groq — gratuito, muito rápido
GROQ_API_KEY=sua_chave_aqui

# Opção 2: OpenAI — busca por significado + palavras
OPENAI_API_KEY=sua_chave_aqui
```

> Você pode pegar uma chave Groq gratuitamente em [console.groq.com](https://console.groq.com).

### 3. Subir o banco e rodar a aplicação

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

Depois de rodar, acesse:

- **Interface:** http://127.0.0.1:5173
- **API (documentação interativa):** http://127.0.0.1:8084/api/docs

---

## Testes

```bash
python -m pytest -v
```

---

## Licença

MIT — projeto de portfólio.
