from __future__ import annotations

import os
from uuid import uuid4

import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector

from ..core.chunking import lexical_query


class DocumentsRepository:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.environ.get(
            "DATABASE_URL",
            "postgresql://docmind:docmind@127.0.0.1:5436/docmind",
        )

    def connect(self):
        conn = psycopg.connect(self.dsn, row_factory=dict_row)
        register_vector(conn)
        return conn

    def initialize(self):
        # A extensão precisa existir antes de registrar o tipo vector na conexão.
        with psycopg.connect(self.dsn) as connection:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")

        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY, name TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id BIGSERIAL PRIMARY KEY,
                    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    page INTEGER NOT NULL, text TEXT NOT NULL,
                    embedding VECTOR(1536),
                    search_vector TSVECTOR GENERATED ALWAYS AS
                        (to_tsvector('simple', text)) STORED
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS chunks_search_idx "
                "ON chunks USING GIN(search_vector)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS chunks_document_idx ON chunks(document_id)"
            )

    def add_document(
        self,
        name: str,
        chunks: list[tuple[int, str]],
        embeddings: list[list[float]] | None = None,
    ) -> tuple[str, int]:
        if not chunks:
            raise ValueError("O arquivo não contém texto pesquisável")

        if len(chunks) > 300:
            raise ValueError("Documento grande demais (máximo de 300 trechos)")

        if embeddings is not None and len(embeddings) != len(chunks):
            raise ValueError("Número de embeddings diferente dos trechos")

        document_id = str(uuid4())
        chunk_records = [
            (
                document_id,
                page,
                text,
                np.array(embeddings[i], dtype=np.float32) if embeddings is not None else None,
            )
            for i, (page, text) in enumerate(chunks)
        ]

        with self.connect() as db:
            db.execute("INSERT INTO documents(id, name) VALUES (%s, %s)", (document_id, name))
            with db.cursor() as cur:
                cur.executemany(
                    "INSERT INTO chunks(document_id, page, text, embedding) "
                    "VALUES (%s, %s, %s, %s)",
                    chunk_records,
                )
        return document_id, len(chunks)

    def list_documents(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute("""
                SELECT d.id::text AS id, d.name, d.created_at,
                       COUNT(c.id)::integer AS chunks
                FROM documents d LEFT JOIN chunks c ON c.document_id=d.id
                GROUP BY d.id ORDER BY d.created_at DESC
            """).fetchall()
            return rows

    def document_chunks(
        self,
        document_id: str,
        limit: int = 20,
    ) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT d.name AS document, c.page, c.text
                FROM chunks c JOIN documents d ON d.id=c.document_id
                WHERE c.document_id=%s
                ORDER BY c.id
                LIMIT %s
                """,
                (document_id, limit),
            ).fetchall()
        return [{"number": index, **row} for index, row in enumerate(rows, start=1)]

    def delete_document(self, document_id: str) -> bool:
        with self.connect() as db:
            result = db.execute("DELETE FROM documents WHERE id=%s", (document_id,))
            return result.rowcount > 0

    def search(
        self,
        question: str,
        document_id: str | None = None,
        embedding: list[float] | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Combina busca textual e vetorial e filtra pelo documento, quando informado."""
        query = lexical_query(question)

        vector = np.array(embedding, dtype=np.float32) if embedding is not None else None
        if not query and vector is None:
            return []

        safe_lexical = query if query else ""

        with self.connect() as db:
            if safe_lexical:
                sql = """
                    WITH candidates AS (
                        SELECT c.page, c.text, d.name AS document,
                          ts_rank_cd(c.search_vector, to_tsquery('simple', %s)) AS lexical,
                          CASE WHEN %s::vector IS NOT NULL AND c.embedding IS NOT NULL
                            THEN GREATEST(0, 1-(c.embedding <=> %s::vector))
                            ELSE 0 END AS semantic
                        FROM chunks c JOIN documents d ON d.id=c.document_id
                        WHERE (%s::uuid IS NULL OR c.document_id=%s::uuid)
                    )
                    SELECT document, page, text, lexical, semantic,
                        (0.35 * LEAST(lexical*5, 1) + 0.65 * semantic) AS score
                    FROM candidates
                    WHERE lexical > 0 OR semantic > 0.53
                    ORDER BY score DESC LIMIT %s
                """
                params = (safe_lexical, vector, vector, document_id, document_id, limit)
            else:
                sql = """
                    WITH candidates AS (
                        SELECT c.page, c.text, d.name AS document,
                          0.0::float AS lexical,
                          CASE WHEN %s::vector IS NOT NULL AND c.embedding IS NOT NULL
                            THEN GREATEST(0, 1-(c.embedding <=> %s::vector))
                            ELSE 0 END AS semantic
                        FROM chunks c JOIN documents d ON d.id=c.document_id
                        WHERE (%s::uuid IS NULL OR c.document_id=%s::uuid)
                    )
                    SELECT document, page, text, lexical, semantic,
                        semantic AS score
                    FROM candidates
                    WHERE semantic > 0.53
                    ORDER BY score DESC LIMIT %s
                """
                params = (vector, vector, document_id, document_id, limit)

            rows = db.execute(sql, params).fetchall()

        return [
            {
                "number": index,
                "document": row["document"],
                "page": row["page"],
                "text": row["text"],
                "score": round(float(row["score"]), 3),
            }
            for index, row in enumerate(rows, start=1)
        ]
