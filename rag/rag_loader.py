"""
Load documents from disk (or other sources) into text chunks.
Supports: .txt, .md, .markdown, .pdf (if pypdf installed).
Returns list of dict: {"id": str, "text": str, "metadata": {...}}
"""
import os
import uuid
from typing import List, Dict, Optional

try:
    import pypdf  # type: ignore
    _HAS_PYPDF = True
except Exception:
    _HAS_PYPDF = False

def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _read_pdf(path: str) -> str:
    if not _HAS_PYPDF:
        raise RuntimeError("pypdf not installed; cannot read PDF files")
    text_parts = []
    reader = pypdf.PdfReader(path)
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)

def load_documents_from_paths(paths: List[str], namespace: Optional[str] = None) -> List[Dict]:
    """
    Load documents from the filesystem. `paths` can be files or directories.
    Returns list of {"id","text","metadata"}.
    """
    docs = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for fn in files:
                    full = os.path.join(root, fn)
                    docs.extend(load_documents_from_paths([full], namespace=namespace))
            continue
        if not os.path.exists(p):
            continue
        ext = os.path.splitext(p)[1].lower()
        try:
            if ext in (".txt", ".md", ".markdown"):
                text = _read_text_file(p)
            elif ext == ".pdf":
                text = _read_pdf(p)
            else:
                # fallback: try to read as text
                text = _read_text_file(p)
        except Exception:
            # skip unreadable files
            continue
        doc_id = f"{namespace + ':' if namespace else ''}{uuid.uuid4().hex}"
        meta = {"source": p, "filename": os.path.basename(p)}
        docs.append({"id": doc_id, "text": text, "metadata": meta})
    return docs