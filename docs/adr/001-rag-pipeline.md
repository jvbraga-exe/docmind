# ADR-001 — Por que FastAPI + LangChain?

**Status:** aceita

## O problema

Precisei de um backend que:
- Recebesse arquivos PDF e TXT
- Dividisse o conteúdo em pedaços e indexasse no banco
- Fizesse busca nesses pedaços quando o usuário perguntasse algo
- Enviasse o resultado para uma IA gerar a resposta

A questão era: usar as bibliotecas do ecossistema de IA (como o LangChain) ou escrever tudo do zero?

## O que decidi

Usar **FastAPI + LangChain**, organizados em camadas separadas para facilitar manutenção e testes.

### Como o código está organizado

1. **`app/api/`** — Recebe as requisições HTTP, valida o que chegou e repassa para os serviços. Nada de lógica de negócio aqui.

2. **`app/core/chunking.py`** — Divide os documentos em pedaços menores usando o `RecursiveCharacterTextSplitter` do LangChain. Ele tenta não cortar no meio de uma frase — respeita parágrafos e pontuação.

3. **`app/services/ai_provider.py`** — É quem fala com a IA (Groq ou OpenAI). Usa os componentes oficiais do LangChain para montar o prompt, enviar para o modelo e receber a resposta.

4. **`app/services/`** — Dois serviços principais:
   - `DocumentService`: cuida do upload e da indexação
   - `AnswerService`: cuida de buscar os trechos certos e gerar a resposta

5. **`app/repositories/`** — Toda a comunicação com o banco de dados fica aqui, separada do resto.

## Por que essa escolha faz sentido

- **LangChain** tem exatamente os componentes que precisamos prontos e bem mantidos. Usar o `RecursiveCharacterTextSplitter`, o `ChatGroq` e o `OpenAIEmbeddings` é mais confiável do que reescrever do zero.
- **Separar em camadas** significa que podemos testar cada parte isoladamente sem precisar de banco ou de IA de verdade — a suíte de testes roda em frações de segundo por isso.
- **FastAPI** com código assíncrono significa que o servidor consegue atender várias requisições ao mesmo tempo sem travar enquanto espera o banco ou a IA responder.
