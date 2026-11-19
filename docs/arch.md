# Como o DocMind funciona por dentro

> Este documento explica a arquitetura do projeto em ordem cronológica de execução — do momento em que o usuário sobe um arquivo até a resposta aparecer na tela.

---

## Visão geral

O DocMind tem dois fluxos principais:

1. **Indexação** — quando você sobe um documento
2. **Consulta** — quando você faz uma pergunta

Cada um passa por camadas bem separadas: a rota HTTP recebe o pedido, um serviço cuida da lógica, o banco de dados guarda ou busca os dados, e a IA processa o texto.

```
[ Navegador / Frontend ]
        │
        ▼
[ API HTTP — FastAPI ]
        │
        ▼
[ Serviços — DocumentService / AnswerService ]
        │              │
        ▼              ▼
[ Banco de dados ]  [ IA — Groq ou OpenAI ]
 PostgreSQL
```

---

## Fluxo 1 — Indexar um documento

### Passo 1 — O arquivo chega na API

Arquivo: [`app/api/routes.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/api/routes.py)

O usuário seleciona um PDF ou TXT na interface e clica em "Indexar documento". O frontend envia o arquivo para o endpoint `POST /api/documents`.

A rota faz duas verificações rápidas antes de qualquer coisa:
- É `.pdf` ou `.txt`? Se não, devolve erro 400.
- Tem mais de 8 MB? Se sim, devolve erro 413.

Se passar, repassa tudo para o `DocumentService`.

---

### Passo 2 — Extrair o texto

Arquivo: [`app/services/extraction.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/extraction.py)

O serviço chama `extract_chunks()`, que:

- Para **PDF**: usa a biblioteca `pypdf` para ler o texto de cada página. Limite: 80 páginas.
- Para **TXT**: decodifica o arquivo como UTF-8.

Se o arquivo não tiver texto pesquisável (ex: PDF com imagem escaneada sem OCR), lança um erro.

---

### Passo 3 — Dividir em pedaços (chunks)

Arquivo: [`app/core/chunking.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/core/chunking.py)

Textos longos não cabem no limite de contexto da IA de uma vez. Por isso, `chunks_from_pages()` divide o texto em pedaços menores usando o `RecursiveCharacterTextSplitter` do LangChain.

**Como o splitter funciona:**
- Cada pedaço tem no máximo **850 caracteres**.
- Os pedaços têm uma **sobreposição de 100 caracteres** entre um e o próximo. Isso evita que uma informação importante fique cortada bem na divisa entre dois pedaços.
- Ele tenta cortar nos lugares certos: primeiro tenta separar em `\n\n` (parágrafo), depois `\n` (linha), depois espaço, e só no último caso corta no meio de uma palavra.

Cada pedaço sai como uma tupla `(número_da_página, texto)` para saber de onde veio.

> **Exemplo:** um PDF de 3 páginas com texto denso pode virar ~20 chunks, cada um com seu número de página registrado.

---

### Passo 4 — Gerar embeddings (só com OpenAI)

Arquivo: [`app/services/documents.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/documents.py) · [`app/services/ai_provider.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/ai_provider.py)

Se você configurou uma `OPENAI_API_KEY`, o sistema chama `ai.embed()` para transformar o texto de cada chunk em um vetor numérico — uma lista de 1536 números que representa o *significado* daquele trecho.

Se você usa **Groq**, esse passo é pulado. A Groq não oferece esse serviço, então os chunks são salvos sem vetor. A busca será feita por palavras no lugar.

---

### Passo 5 — Salvar no banco

Arquivo: [`app/repositories/documents.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/repositories/documents.py)

O `DocumentsRepository.add_document()` salva tudo no PostgreSQL em duas tabelas:

**Tabela `documents`** — uma linha por documento:
| id (UUID) | name | created_at |
|---|---|---|
| `abc-123` | `CV.pdf` | `2026-11-18 19:01` |

**Tabela `chunks`** — uma linha por pedaço:
| id | document_id | page | text | embedding | search_vector |
|---|---|---|---|---|---|
| 1 | `abc-123` | 1 | "Trabalhou em..." | `[0.12, -0.04, ...]` ou NULL | gerado automaticamente |

A coluna `search_vector` é gerada automaticamente pelo PostgreSQL a partir do texto — ela é o que permite a busca por palavras depois. Um índice `GIN` sobre ela torna essa busca muito rápida.

**Ao final**, o frontend recebe de volta:
```json
{ "id": "abc-123", "name": "CV.pdf", "chunks": 8 }
```

---

## Fluxo 2 — Fazer uma pergunta

### Passo 1 — A pergunta chega na API

Arquivo: [`app/api/routes.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/api/routes.py)

O usuário digita uma pergunta e clica em "Consultar documentos". O frontend envia um `POST /api/ask` com o texto da pergunta e (opcionalmente) o ID do documento selecionado.

A rota repassa para o `AnswerService`.

---

### Passo 2 — Decidir em qual documento buscar

Arquivo: [`app/services/answers.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/answers.py)

Se o usuário não escolheu um documento específico mas só existe um na biblioteca, o sistema usa ele automaticamente. Isso evita que o usuário precise selecionar quando tem um arquivo só.

---

### Passo 3 — Detectar se é pedido de resumo

Arquivo: [`app/services/answers.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/answers.py)

A função `_asks_for_overview()` verifica se a pergunta parece um pedido de visão geral do documento, como:

> "resuma o documento", "o que tem aqui?", "fale sobre meu currículo"

Se for, o sistema pula a busca e pega diretamente os primeiros 20 chunks do documento (na ordem) para dar uma visão completa para a IA.

---

### Passo 4 — Buscar os trechos relevantes

Arquivo: [`app/repositories/documents.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/repositories/documents.py)

Se não for pedido de resumo, o sistema chama `repository.search()`. O que acontece aqui depende do seu provedor de IA:

#### Com Groq (busca por palavras)

A função `lexical_query()` em `chunking.py` prepara os termos da pergunta:
- Remove palavras curtas (menos de 3 letras), pontuação e palavras comuns
- Monta uma expressão de busca: `"qual | numero | telefone"`

O PostgreSQL usa essa expressão para procurar nos `search_vector` de todos os chunks e ordena os resultados por relevância.

#### Com OpenAI (busca combinada)

Além da busca por palavras, o sistema também gera um embedding da pergunta e compara matematicamente com os embeddings de cada chunk. O resultado final combina os dois:

```
Score final = (35% × relevância por palavras) + (65% × similaridade de significado)
```

Apenas chunks com pontuação acima de zero aparecem no resultado.

---

### Passo 5 — Fallback quando a busca não acha nada

Arquivo: [`app/services/answers.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/answers.py)

Às vezes a busca por palavras não encontra nada porque os termos da pergunta não aparecem literalmente no documento.

> **Exemplo real:** o usuário pergunta *"qual é o meu número de telefone?"*, mas no documento está escrito só o número `(11) 0000-0000` sem a palavra "telefone" em lugar nenhum.

Quando isso acontece e há um documento-alvo selecionado, o sistema usa o plano B: carrega todos os chunks do documento e manda para a IA avaliar. A IA consegue encontrar o número mesmo assim porque ela lê o contexto completo.

Se não houver nenhum documento-alvo e a busca retornar vazia, a resposta é:
> *"Não encontrei trechos relevantes nos documentos para responder."*

---

### Passo 6 — A IA monta a resposta

Arquivo: [`app/services/ai_provider.py`](file:///c:/Users/langd/Documents/Repos/docmind/app/services/ai_provider.py)

Os trechos encontrados são formatados assim antes de ir para a IA:

```
[1] Documento: CV.pdf | Página: 2
Contato: (11) 0000-0000 | email@exemplo.com

[2] Documento: NF-e.pdf | Página: 1
Formado em Ciência da Computação pela...
```

Esse bloco vai junto com a pergunta do usuário para o modelo de IA (Groq ou OpenAI GPT). O prompt instrui a IA a:

- Responder só com o que está nos trechos — não inventar nada
- Citar os trechos usados com `[1]`, `[2]` etc.
- Responder em português e ir direto ao ponto
- Dizer que não encontrou se a informação não estiver ali

A IA processa e devolve o texto da resposta.

---

### Passo 7 — O resultado volta para o usuário

A resposta final vai de volta para o frontend assim:

```json
{
  "answer": "O número de telefone é (11) 0000-0000 [1].",
  "sources": [
    {
      "number": 1,
      "document": "NF-e.pdf",
      "page": 2,
      "text": "Contato: (11) 0000-0000 | email@exemplo.com",
      "score": 0.0
    }
  ]
}
```

O frontend renderiza o texto da resposta em Markdown, transforma os `[1]` em badges clicáveis e exibe cada source como um card com o nome do arquivo e a página.

---

## Como os arquivos se encaixam

```
docmind/
├── app/
│   ├── main.py                  — inicializa o servidor e injeta as dependências
│   ├── schemas.py               — define o formato da pergunta (Pydantic)
│   ├── api/
│   │   └── routes.py            — endpoints HTTP: /documents e /ask
│   ├── core/
│   │   └── chunking.py          — divide texto em pedaços e prepara busca léxica
│   ├── services/
│   │   ├── extraction.py        — lê PDF/TXT e valida os arquivos
│   │   ├── documents.py         — orquestra o upload: extrai → embed → salva
│   │   ├── answers.py           — orquestra a consulta: busca → fallback → IA
│   │   └── ai_provider.py       — fala com Groq ou OpenAI via LangChain
│   └── repositories/
│       └── documents.py         — toda comunicação com o PostgreSQL fica aqui
├── frontend/                    — interface React + TypeScript
├── tests/                       — 19 testes unitários (rodam sem banco nem IA)
└── docker-compose.yml           — sobe o PostgreSQL com pgvector
```

---

## Por que cada camada é separada?

Cada camada conhece só a camada abaixo dela — a rota não fala direto com o banco, o serviço não sabe que existe HTTP, o repositório não sabe que existe IA.

Isso tem um benefício prático imediato: **os testes não precisam de banco real nem de chave de API**. Os serviços recebem objetos falsos (mocks) nos testes, e a suíte inteira roda em menos de 1 segundo.
