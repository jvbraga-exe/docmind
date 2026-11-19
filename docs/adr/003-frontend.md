# ADR-003 — Interface do usuário

**Status:** aceita

## O que a interface precisa fazer

O DocMind tem um fluxo simples: você sobe um arquivo, faz uma pergunta e recebe uma resposta com referências. A interface foi pensada para deixar esse fluxo o mais direto possível.

## Como está organizada

Tudo fica em uma única tela dividida em duas partes:

**Coluna da esquerda — seus documentos:**
- Upload de arquivos PDF ou TXT
- Lista dos documentos indexados com a data e a quantidade de trechos
- Botão para remover um documento

**Coluna da direita — perguntas e respostas:**
- Campo para digitar a pergunta
- Seletor para escolher em qual documento buscar (ou em todos ao mesmo tempo)
- Área de resposta com o texto gerado pela IA em Markdown
- Seção de fontes: cada trecho que embasou a resposta aparece com o nome do arquivo e a página de origem

## Por que essas escolhas

A ideia é que o usuário sempre saiba de onde veio a informação. A IA pode errar ou interpretar algo fora de contexto — por isso os trechos originais ficam visíveis logo abaixo da resposta, para qualquer pessoa conferir na hora.

A interface é construída com React, TypeScript e Tailwind CSS, e se comunica com o backend via API — as duas partes são completamente independentes entre si.
