# ADR-002 — Como o DocMind encontra trechos nos documentos

**Status:** aceita

## Contexto

Uma busca por palavras pode deixar passar um trecho escrito de outro jeito. Já uma busca que compara o sentido do texto pode não encontrar nomes, siglas ou termos exatos.

## Decisão

Guardamos documentos, trechos e suas representações numéricas no PostgreSQL. O `pgvector` compara essas representações para encontrar trechos com sentido parecido; a busca por palavras também entra no resultado. A combinação dá mais peso à busca por sentido (65%) e menos à busca por palavras (35%).

Para perguntas específicas, retornamos até cinco trechos. Quando a pessoa pede um resumo de um documento selecionado, retornamos até vinte.

Com Groq, que é a configuração usada no projeto, a busca é por palavras; o modelo recebe os trechos encontrados e escreve a resposta. A busca por similaridade e a combinação de pesos só são usadas quando o provedor também oferece embeddings, como na configuração com OpenAI.

## Alternativas

Um serviço separado só para comparar textos exigiria mais configuração e manutenção. Busca aproximada, uma etapa extra para reordenar os resultados ou o uso de agentes também deixariam o sistema mais complexo sem necessidade para este projeto.

## Consequências

Os documentos e as buscas ficam no PostgreSQL, e o envio do arquivo salva tudo em uma transação. Os pesos da busca são iniciais: ainda não foram avaliados com um conjunto de perguntas de teste. Sem chave de IA para gerar as representações numéricas, o sistema busca apenas pelas palavras. PDFs que são só imagens não funcionam, porque o projeto ainda não transforma imagem em texto (OCR).
