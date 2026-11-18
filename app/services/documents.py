from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from ..repositories.documents import DocumentsRepository
    from .ai_provider import AIProvider

from .extraction import extract_chunks


class DocumentService:
    def __init__(self, repository: DocumentsRepository, ai: AIProvider):
        self.repository = repository
        self.ai = ai

    async def upload(self, filename: str, contents: bytes) -> dict:
        chunks = await run_in_threadpool(extract_chunks, filename, contents)

        vectors = (
            await self.ai.embed([text for _, text in chunks])
            if self.ai.embedding_enabled
            else None
        )
        document_id, count = await run_in_threadpool(
            self.repository.add_document,
            Path(filename).name,
            chunks,
            vectors,
        )
        return {
            'id': document_id,
            'name': Path(filename).name,
            'chunks': count,
            'mode': 'hybrid' if vectors else 'lexical',
        }

    async def list(self) -> list[dict]:
        return await run_in_threadpool(self.repository.list_documents)

    async def delete(self, document_id: str) -> bool:
        return await run_in_threadpool(self.repository.delete_document, document_id)
