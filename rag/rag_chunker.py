"""
Chunk text for RAG. Simple sliding-window chunker with overlap (token-agnostic).
You can later replace it by a token-aware chunker using core.tokenizer.
"""
from typing import List, Tuple

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Tuple[str, int, int]]:
    """
    Splits text into chunks of approximately chunk_size characters with overlap.
    Returns list of tuples: (chunk_text, start_idx, end_idx)
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap >= chunk_size:
        overlap = int(chunk_size * 0.1)

    text = text.strip()
    n = len(text)
    if n == 0:
        return []

    chunks = []
    start = 0
    while start < n:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append((chunk, start, min(end, n)))
        if end >= n:
            break
        start = end - overlap
    return chunks

def chunk_document(doc: dict, chunk_size: int = 1000, overlap: int = 200) -> List[dict]:
    """
    doc: {"id", "text", "metadata"}
    Returns list of chunk dicts: {"id": f"{doc_id}:{i}", "text": chunk, "metadata": {..., 'source_id': doc_id, 'start':.., 'end':..}}
    """
    chunks = []
    parts = chunk_text(doc.get("text", ""), chunk_size=chunk_size, overlap=overlap)
    for i, (txt, s, e) in enumerate(parts):
        cid = f"{doc['id']}::chunk::{i}"
        meta = dict(doc.get("metadata", {}))
        meta.update({"source_id": doc["id"], "chunk_index": i, "start": s, "end": e})
        chunks.append({"id": cid, "text": txt, "metadata": meta})
    return chunks