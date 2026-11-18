from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from ..core.chunking import chunks_from_pages

MAX_BYTES = 8 * 1024 * 1024
MAX_PAGES = 80
MAX_CHUNKS = 300


def extract_chunks(filename: str, content: bytes) -> list[tuple[int, str]]:
    suffix = Path(filename).suffix.lower()
    if suffix not in {'.pdf', '.txt'}:
        raise ValueError('Envie um arquivo .pdf ou .txt')

    if len(content) > MAX_BYTES:
        raise ValueError('Arquivo maior que 8 MB')

    if suffix == '.pdf':
        pdf = PdfReader(BytesIO(content))
        if len(pdf.pages) > MAX_PAGES:
            raise ValueError('PDF excede 80 páginas')
        pages = [page.extract_text() or '' for page in pdf.pages]
    else:
        pages = [content.decode('utf-8-sig')]

    chunks = chunks_from_pages(pages)

    if not chunks:
        raise ValueError('Arquivo sem texto pesquisável')

    if len(chunks) > MAX_CHUNKS:
        raise ValueError('Documento excede 300 trechos')

    return chunks
