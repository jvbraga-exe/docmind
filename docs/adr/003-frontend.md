# ADR-003 — Biblioteca e consulta na mesma tela

**Status:** aceita

## Decisão

A tela reúne a biblioteca de arquivos, o envio de documentos e a consulta com suas fontes. O front-end usa React, TypeScript e Tailwind. Ele roda e pode ser publicado separado do FastAPI; os dois se comunicam pela API HTTP.

## Consequências

No desenvolvimento, o Vite encaminha as chamadas da interface para a API. Em produção, o endereço da API e a origem permitida são configurados pelo ambiente. Como o backend não guarda o histórico das conversas, a interface mostra apenas a resposta atual. Também exibimos os trechos usados para que a pessoa possa conferir a resposta da IA.
