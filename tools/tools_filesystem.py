"""
Safe filesystem helpers with a base directory restriction to avoid accidental escape.
Functions:
- safe_read_file(path, base_dir=None) -> text
- safe_write_file(path, content, base_dir=None, overwrite=False) -> True
- list_files(path, base_dir=None) -> list[str]
"""
from pathlib import Path
import logging
from typing import Optional, List

logger = logging.getLogger("tools.filesystem")


def _resolve_within_base(path: str, base_dir: Optional[str]) -> Path:
    p = Path(path).expanduser().resolve()
    if base_dir:
        base = Path(base_dir).expanduser().resolve()
        try:
            p.relative_to(base)
        except Exception:
            raise PermissionError(f"Path {p} is outside of allowed base directory {base}")
    return p


def safe_read_file(path: str, base_dir: Optional[str] = None, max_bytes: int = 10_000_000) -> str:
    p = _resolve_within_base(path, base_dir)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(str(p))
    size = p.stat().st_size
    if size > max_bytes:
        raise IOError("File too large")
    return p.read_text(encoding="utf-8", errors="ignore")


def safe_write_file(path: str, content: str, base_dir: Optional[str] = None, overwrite: bool = False) -> bool:
    p = _resolve_within_base(path, base_dir)
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return True


def list_files(path: str, base_dir: Optional[str] = None, recursive: bool = False) -> List[str]:
    p = _resolve_within_base(path, base_dir)
    if not p.exists():
        return []
    if p.is_file():
        return [str(p)]
    if recursive:
        return [str(x) for x in p.rglob("*") if x.is_file()]
    return [str(x) for x in p.iterdir() if x.is_file()]