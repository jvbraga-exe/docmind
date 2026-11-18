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
        embedding = None

        if self.ai.embedding_enabled and not overview_question:
            embedding = (await self.ai.embed([question]))[0]

        if overview_question and document_id is None:
            documents = await run_in_threadpool(self.repository.list_documents)
            if len(documents) == 1:
                document_id = documents[0]['id']

        if overview_question and document_id is not None:
            sources = await run_in_threadpool(self.repository.document_chunks, document_id)
        else:
            sources = await run_in_threadpool(
                self.repository.search, question, document_id, embedding
            )
        if not sources:
            return {'answer': 'Não encontrei trechos relevantes.', 'mode': 'search', 'sources': []}
        if not self.ai.enabled:
            return {
                'answer': 'Trechos recuperados. Configure uma chave de IA para gerar uma resposta.',
                'mode': 'search', 'sources': sources,
            }
        return {
            'answer': await self.ai.answer(question, sources),
            'mode': 'generated', 'sources': sources,
        }


def _asks_for_overview(question: str) -> bool:
    normalized = unicodedata.normalize('NFKD', question.lower())
    normalized = ''.join(char for char in normalized if not unicodedata.combining(char))
    normalized = re.sub(r'[^a-z0-9]+', ' ', normalized).strip()
    overview_phrases = (
        'o que tem',
        'o que consta',
        'resuma',
        'resumo',
        'fale sobre',
        'me fale',
        'me conte',
        'meu curriculo',
        'esse documento',
        'este documento',
    )
    return any(phrase in normalized for phrase in overview_phrases)
