# ADR-002 — Como o DocMind busca informações nos documentos

**Status:** aceita

## O problema

Quando o usuário faz uma pergunta, o sistema precisa encontrar os trechos certos do documento antes de enviar para a IA. Mas nem sempre a palavra que o usuário usa aparece exatamente no documento.

Exemplo: o usuário pergunta *"qual é o meu telefone?"*, mas no documento está escrito só o número `(11) 94606-1445`, sem a palavra "telefone" em nenhum lugar. Uma busca por palavra exata não encontra nada.

Existem dois jeitos de resolver isso:

**Busca por palavras (léxica):** procura exatamente o que foi digitado. Ótimo para números, nomes, siglas e qualquer termo específico. Falha quando o usuário usa sinônimos ou faz uma pergunta indireta.

**Busca por significado (semântica):** converte a pergunta e os trechos em números que representam o significado, e compara matematicamente. Consegue entender que *"remuneração"* e *"salário"* falam da mesma coisa. Precisa de um modelo de embeddings (OpenAI tem esse serviço; Groq não).

## O que decidimos

O DocMind suporta os dois provedores de IA, e cada um usa uma estratégia de busca:

### Modo Groq — busca por palavras + fallback

O Groq não oferece geração de embeddings, então a busca é feita pelo PostgreSQL usando as palavras da pergunta diretamente.

Para resolver o problema do "telefone sem a palavra telefone", adicionamos um fallback: se a busca por palavras não encontrar nada mas o usuário está consultando um documento específico, o sistema carrega todos os trechos desse documento e manda para a IA avaliar. Assim o Groq consegue responder mesmo quando os termos não coincidem exatamente.

### Modo OpenAI — busca combinada (palavras + significado)

Quando o `OPENAI_API_KEY` está configurado:
- Cada trecho do documento ganha uma representação matemática do seu significado (embedding), salva no banco.
- A pergunta do usuário também vira um embedding na hora da busca.
- O sistema combina os dois resultados: 65% de peso para similaridade de significado e 35% para correspondência de palavras.
- Isso garante que tanto perguntas conceituais quanto termos técnicos exatos sejam encontrados.

## Por que não usamos um banco de vetores separado?

Consideramos ferramentas como Pinecone e Qdrant, mas o PostgreSQL com a extensão `pgvector` resolve o problema sem adicionar mais uma peça na infraestrutura. Documentos, trechos, vetores e índices de texto ficam todos no mesmo lugar — mais simples de rodar, de fazer backup e de entender.
