"""
Preprocess utilities:
- clean_text(text) -> remove control chars, normalize whitespace
- chunk_text_by_chars(text, chunk_size, overlap) -> list of chunks
- prepare_document(doc, text_fields) -> returns {'id','text','metadata'}
"""

import re
from typing import List, Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger("datasets.preprocess")


_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(text: str) -> str:
    if text is None:
        return ""
    txt = _CTRL_RE.sub(" ", text)
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt)
    return txt.strip()


def chunk_text_by_chars(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split text into chunks with overlap. Returns list of dict: {'id','text','start','end'}.
    """
    text = text or ""
    if not text:
        return []
    n = len(text)
    chunks = []
    i = 0
    idx = 0
    while i < n:
        end = min(i + chunk_size, n)
        chunk_text = text[i:end]
        chunks.append({"id": f"chunk_{uuid.uuid4().hex}", "text": chunk_text, "start": i, "end": end, "index": idx})
        idx += 1
        if end >= n:
            break
        i = end - overlap
    return chunks


def prepare_document(raw: Dict[str, Any], text_fields: Optional[List[str]] = None, id_field: Optional[str] = None) -> Dict[str, Any]:
    """
    Normalize raw record into a document with 'id', 'text', 'metadata'.
    - text_fields: list of candidate fields to join into text (default: ['text','content','body'])
    - id_field: optional field name in raw to use as id; otherwise uuid
    """
    tf = text_fields or ["text", "content", "body", "description"]
    parts = []
    for k in tf:
        v = raw.get(k)
        if v:
            parts.append(str(v))
    if not parts:
        # try entire object as JSON
        import json
        parts = [json.dumps(raw, ensure_ascii=False)]
    text = clean_text("\n\n".join(parts))
    doc_id = (str(raw.get(id_field)) if id_field and raw.get(id_field) else f"doc_{uuid.uuid4().hex}")
    metadata = {k: raw.get(k) for k in raw.keys() if k not in tf}
    return {"id": doc_id, "text": text, "metadata": metadata}