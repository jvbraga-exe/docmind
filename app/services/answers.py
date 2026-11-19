from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING

from fastapi.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from ..repositories.documents import DocumentsRepository
    from .ai_provider import AIProvider


class AnswerService:
    def __init__(self, repository: DocumentsRepository, ai: AIProvider):
        self.repository = repository
        self.ai = ai

    async def ask(self, question: str, document_id: str | None = None) -> dict:
        overview_question = _asks_for_overview(question)

        # Se não especificou documento e só existe 1 documento na biblioteca, usa ele como alvo
        if document_id is None:
            documents = await run_in_threadpool(self.repository.list_documents)
            if len(documents) == 1:
                document_id = documents[0]["id"]

        # Gera embedding vetorial se o provedor tiver suporte (OpenAI)
        embedding = None
        if self.ai.embedding_enabled and not overview_question:
            embedding = await self.ai.embed_query(question)

        # 1. Recuperação primária:
        # Se for pedido de visão geral/resumo, busca os trechos do documento; senão, faz busca híbrida/léxica
        if overview_question and document_id is not None:
            sources = await run_in_threadpool(self.repository.document_chunks, document_id)
        else:
            sources = await run_in_threadpool(
                self.repository.search, question, document_id, embedding
            )

        # 2. Fallback resiliente:
        # Se a busca por termos exatos não encontrou nada (ex: o usuário perguntou por 'telefone',
        # mas no documento só consta o número bruto '(11) 9xxxx-xxxx' sem a palavra 'telefone'),
        # e temos um documento alvo selecionado, recuperamos os trechos do documento para a IA avaliar.
        if not sources and document_id is not None:
            sources = await run_in_threadpool(self.repository.document_chunks, document_id)

        if not sources:
            return {
                "answer": "Não encontrei trechos relevantes nos documentos para responder.",
                "sources": [],
            }

        # Envia os trechos para a IA (Groq ou OpenAI) sintetizar a resposta com referências
        answer = await self.ai.answer(question, sources)
        return {
            "answer": answer,
            "sources": sources,
        }


def _normalize_for_match(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text.lower())
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", ascii_only).strip()


def _asks_for_overview(question: str) -> bool:
    normalized = _normalize_for_match(question)
    overview_phrases = (
        "o que tem",
        "o que consta",
        "resuma",
        "resumo",
        "fale sobre",
        "me fale",
        "me conte",
        "meu curriculo",
        "esse documento",
        "este documento",
    )
    return any(phrase in normalized for phrase in overview_phrases)
