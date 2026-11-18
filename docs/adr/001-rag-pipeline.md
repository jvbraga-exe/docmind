# ADR-001 — Como o DocMind organiza o trabalho com documentos

**Status:** aceita

## Contexto

No começo, as rotas cuidavam de tudo: recebiam arquivos, liam PDFs, consultavam o banco e chamavam a IA. Isso deixava o código difícil de testar sem depender do banco ou de um serviço externo.

## Decisão

As rotas recebem as requisições e devolvem as respostas HTTP. O Pydantic valida os dados recebidos. `DocumentService` cuida do envio e da preparação dos arquivos para busca; `AnswerService` cuida das perguntas; `DocumentsRepository` conversa com o banco; e `AIProvider` chama o modelo de IA.

A leitura dos arquivos e a divisão do texto em trechos não dependem do banco. Assim, dá para testar essa parte sem precisar iniciar o PostgreSQL.

## Alternativas

Frameworks de agentes e ferramentas maiores de pipeline adicionariam dependências e etapas que este fluxo não precisa.

## Consequências

Cada parte cuida de uma tarefa. Nos testes, usamos um repositório falso no lugar do banco. Se não houver chave de IA, ainda dá para buscar palavras nos documentos.
