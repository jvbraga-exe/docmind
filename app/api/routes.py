import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pypdf.errors import PdfReadError

from ..schemas import Question
from ..services.answers import AnswerService
from ..services.documents import DocumentService
from ..services.extraction import MAX_BYTES

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def documents_service(request: Request) -> DocumentService:
    return request.app.state.documents


def answers_service(request: Request) -> AnswerService:
    return request.app.state.answers


@router.get("/documents")
async def list_documents(service: DocumentService = Depends(documents_service)):
    return await service.list()


@router.post("/documents", status_code=201)
async def upload(
    file: UploadFile = File(...),
    service: DocumentService = Depends(documents_service),
):
    filename = Path(file.filename or "").name

    if Path(filename).suffix.lower() not in {".pdf", ".txt"}:
        raise HTTPException(400, "Envie um arquivo .pdf ou .txt")

    content = await file.read(MAX_BYTES + 1)

    if len(content) > MAX_BYTES:
        raise HTTPException(413, "Arquivo maior que 8 MB")

    try:
        return await service.upload(filename, content)
    except (ValueError, UnicodeError, PdfReadError) as error:
        raise HTTPException(400, str(error)) from error
    except Exception as error:
        logger.exception("Falha ao indexar documento")
        raise HTTPException(
            502,
            "Falha ao indexar. Confira o banco e a chave de API.",
        ) from error


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(documents_service),
):
    if not await service.delete(str(document_id)):
        raise HTTPException(404, "Documento não encontrado")
    return {"deleted": True}


@router.post("/ask")
async def ask(input: Question, service: AnswerService = Depends(answers_service)):
    try:
        document_id = str(input.document_id) if input.document_id else None
        return await service.ask(input.question, document_id)
    except Exception as error:
        logger.exception("Falha ao consultar documentos")
        raise HTTPException(
            502,
            "Falha na busca ou geração. Verifique banco e API de IA.",
        ) from error
