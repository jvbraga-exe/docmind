import asyncio

import pytest

from app.services.answers import AnswerService
from app.services.documents import DocumentService
from app.services.extraction import MAX_BYTES, extract_chunks


class FakeRepository:
    def __init__(self, sources=None):
        self.sources = sources if sources is not None else [
            {'number': 1, 'document': 'guide.txt', 'page': 1, 'text': 'Kafka reprocessa mensagens.'}
        ]
        self.documents = []

    def search(self, question, document_id, embedding):
        return self.sources

    def document_chunks(self, document_id):
        self.overview_document_id = document_id
        return self.sources

    def add_document(self, name, chunks, vectors):
        doc_id = 'test-doc-id'
        self.documents.append({'id': doc_id, 'name': name, 'chunks': len(chunks)})
        return doc_id, len(chunks)

    def list_documents(self):
        return self.documents

    def delete_document(self, document_id):
        initial = len(self.documents)
        self.documents = [d for d in self.documents if d['id'] != document_id]
        return len(self.documents) < initial or document_id == 'existing-id'


class DisabledAI:
    enabled = False
    embedding_enabled = False

    async def embed(self, texts):
        raise AssertionError('A busca sem IA não deve gerar embeddings')


class EnabledAI:
    enabled = True
    embedding_enabled = True

    def __init__(self):
        self.embedding_calls = 0

    async def embed(self, texts):
        self.embedding_calls += 1
        return [[0.1] * 1536 for _ in texts]

    async def answer(self, question, sources):
        return f"Resposta sintetizada para: {question}"


def test_answers_without_key_returns_excerpts():
    service = AnswerService(FakeRepository(), DisabledAI())
    result = asyncio.run(service.ask('O que faz Kafka?'))
    assert result['mode'] == 'search'
    assert result['sources'][0]['page'] == 1
    assert 'Configure uma chave de IA' in result['answer']


def test_answers_with_no_sources_returns_not_found():
    service = AnswerService(FakeRepository(sources=[]), DisabledAI())
    result = asyncio.run(service.ask('Pergunta sobre algo inexistente?'))
    assert result['mode'] == 'search'
    assert result['sources'] == []
    assert 'Não encontrei trechos relevantes' in result['answer']


def test_answers_with_ai_enabled_generates_response():
    service = AnswerService(FakeRepository(), EnabledAI())
    result = asyncio.run(service.ask('O que faz Kafka?'))
    assert result['mode'] == 'generated'
    assert 'Resposta sintetizada' in result['answer']
    assert len(result['sources']) == 1


def test_overview_uses_all_chunks_of_the_only_document():
    repository = FakeRepository(
        sources=[
            {'number': index, 'document': 'cv.txt', 'page': 1, 'text': f'Trecho {index}'}
            for index in range(1, 9)
        ]
    )
    repository.documents = [{'id': 'test-doc-id'}]
    ai = EnabledAI()

    result = asyncio.run(AnswerService(repository, ai).ask('O que tem no meu currículo?'))

    assert result['mode'] == 'generated'
    assert len(result['sources']) == 8
    assert repository.overview_document_id == 'test-doc-id'
    assert ai.embedding_calls == 0


def test_extraction_rejects_invalid_format():
    with pytest.raises(ValueError, match="Envie um arquivo .pdf ou .txt"):
        extract_chunks('attachment.exe', b'data')
    with pytest.raises(ValueError, match="Envie um arquivo .pdf ou .txt"):
        extract_chunks('data.csv', b'col1,col2\n1,2')


def test_extraction_rejects_oversized_file():
    with pytest.raises(ValueError, match="Arquivo maior que 8 MB"):
        extract_chunks('large.txt', b'x' * (MAX_BYTES + 1))


def test_extraction_rejects_empty_content():
    with pytest.raises(ValueError, match="Arquivo sem texto pesquisável"):
        extract_chunks('empty.txt', b'   \n\t  ')


def test_extraction_accepts_valid_txt():
    chunks = extract_chunks('sample.txt', 'Primeira linha de conteúdo real.'.encode('utf-8'))
    assert len(chunks) == 1
    assert chunks[0] == (1, 'Primeira linha de conteúdo real.')


def test_document_service_upload_and_delete():
    repo = FakeRepository()
    service = DocumentService(repo, DisabledAI())

    upload_result = asyncio.run(
        service.upload('readme.txt', 'Documento de teste com conteúdo.'.encode('utf-8'))
    )
    assert upload_result['name'] == 'readme.txt'
    assert upload_result['chunks'] == 1
    assert upload_result['mode'] == 'lexical'

    docs = asyncio.run(service.list())
    assert len(docs) == 1
    assert docs[0]['name'] == 'readme.txt'

    deleted = asyncio.run(service.delete('existing-id'))
    assert deleted is True
