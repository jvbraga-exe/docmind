import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_text_splitter(
    chunk_size: int = 850,
    chunk_overlap: int = 100,
) -> RecursiveCharacterTextSplitter:
     # Configura o particionador do LangChain
     return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )


def chunk_text(text: str, max_chars: int = 850, overlap: int = 100) -> list[str]:
    """Divide texto usando a estratégia do particionador do LangChain."""
    if max_chars <= overlap or overlap < 0:
        raise ValueError("O tamanho do trecho precisa ser maior que a sobreposição")

    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    splitter = get_text_splitter(chunk_size=max_chars, chunk_overlap=overlap)
    return splitter.split_text(text)


def chunks_from_pages(
    pages: list[str],
    max_chars: int = 850,
    overlap: int = 100,
) -> list[tuple[int, str]]:
    """Gera pares (número_da_página, trecho) mapeando o conteúdo fatiado para cada página."""
    splitter = get_text_splitter(chunk_size=max_chars, chunk_overlap=overlap)
    chunks: list[tuple[int, str]] = []

    for page_number, page_text in enumerate(pages, start=1):
        cleaned = re.sub(r"\s+", " ", page_text).strip()
        if not cleaned:
            continue
        for chunk in splitter.split_text(cleaned):
            chunks.append((page_number, chunk))

    return chunks


def lexical_query(question: str) -> str:
    """Prepara os termos da pergunta para o índice de busca textual do PostgreSQL."""
    terms = re.findall(r"\w{3,}", question.lower(), flags=re.UNICODE)[:12]
    return " | ".join(terms)
