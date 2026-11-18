import re


def chunk_text(text: str, max_chars: int = 850, overlap: int = 100) -> list[str]:
    if max_chars <= overlap or overlap < 0:
        raise ValueError('O tamanho do trecho precisa ser maior que a sobreposição')

    normalized = re.sub(r"\s+", " ", text).strip()

    if not normalized:
        return []

    words = [
        part
        for word in normalized.split()
        for part in (word[index:index + max_chars] for index in range(0, len(word), max_chars))
    ]
    output: list[str] = []
    start = 0

    while start < len(words):
        end = start
        length = 0
        sentence_end = None

        while end < len(words):
            next_length = len(words[end]) + (1 if end > start else 0)
            if end > start and length + next_length > max_chars:
                break
            length += next_length
            end += 1
            if length >= max_chars * 0.6 and words[end - 1][-1:] in {'.', '!', '?'}:
                sentence_end = end

        if end < len(words) and sentence_end is not None:
            end = sentence_end

        fragment = ' '.join(words[start:end])
        if len(fragment) < 40 and output and len(output[-1]) + len(fragment) + 1 <= max_chars:
            output[-1] += ' ' + fragment
        else:
            output.append(fragment)

        if end == len(words):
            break

        next_start = end
        overlap_length = 0
        while next_start > start:
            next_length = len(words[next_start - 1]) + (1 if overlap_length else 0)
            if overlap_length + next_length > overlap:
                break
            overlap_length += next_length
            next_start -= 1
        start = next_start if next_start > start else end

    return output


def chunks_from_pages(pages: list[str]) -> list[tuple[int, str]]:
    return [(page, chunk) for page, text in enumerate(pages, start=1) for chunk in chunk_text(text)]


def lexical_query(question: str) -> str:
    """Usa OR para não exigir que todos os termos apareçam no mesmo trecho."""
    terms = re.findall(r"\w{3,}", question.lower(), flags=re.UNICODE)[:12]
    return " | ".join(terms)
