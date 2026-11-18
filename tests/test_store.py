import pytest

from app.core.chunking import chunk_text, chunks_from_pages, lexical_query


def test_chunking_keeps_page_reference():
    pages = ["A primeira página.", "Kafka entrega eventos. " * 60]
    chunks = chunks_from_pages(pages)
    assert chunks[0] == (1, "A primeira página.")
    assert all(page == 2 for page, _ in chunks[1:])


def test_chunking_trims_blank_and_normalizes_spaces():
    assert chunk_text("   ") == []
    assert chunk_text("  abc   def \n ghi\t ") == ["abc def ghi"]
    long_text = "test " * 400
    chunks = chunk_text(long_text)
    assert len(chunks) > 1
    assert all(len(c) <= 890 for c in chunks)


def test_chunking_keeps_words_and_sentence_boundaries_when_possible():
    assert chunk_text('First sentence. Second sentence.', max_chars=20, overlap=5) == [
        'First sentence.',
        'Second sentence.',
    ]
    assert chunk_text('alpha beta gamma delta epsilon', max_chars=20, overlap=5) == [
        'alpha beta gamma',
        'gamma delta epsilon',
    ]


def test_chunking_rejects_invalid_overlap():
    with pytest.raises(ValueError, match="sobreposição"):
        chunk_text("Some text", max_chars=100, overlap=100)
    with pytest.raises(ValueError, match="sobreposição"):
        chunk_text("Some text", max_chars=100, overlap=120)
    with pytest.raises(ValueError, match="sobreposição"):
        chunk_text("Some text", max_chars=100, overlap=-5)


def test_chunks_from_pages_skips_empty():
    pages = ["", "Valid text", "   "]
    chunks = chunks_from_pages(pages)
    assert len(chunks) == 1
    assert chunks[0] == (2, "Valid text")


def test_lexical_query_filters_punctuation_and_short_terms():
    assert lexical_query("Kafka OR 1=1?") == "kafka"
    assert (
        lexical_query("Como evitar duplicidade no consumidor?")
        == "como | evitar | duplicidade | consumidor"
    )


def test_lexical_query_returns_empty_without_searchable_terms():
    assert lexical_query("de em um") == ""
    assert lexical_query("") == ""
    assert lexical_query("!@#$%^&*()") == ""


def test_lexical_query_limits_number_of_terms():
    long_question = " ".join([f"termo{i}" for i in range(20)])
    terms = lexical_query(long_question).split(" | ")
    assert len(terms) == 12
