import os
import tempfile
import pytest

def test_filesystem_safe_read_write():
    fs = pytest.importorskip("tools.filesystem")
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "f.txt")
        assert fs.safe_write_file(p, "hello", base_dir=d, overwrite=True)
        content = fs.safe_read_file(p, base_dir=d)
        assert "hello" in content
        lst = fs.list_files(d, base_dir=d, recursive=False)
        assert any("f.txt" in x for x in lst)
    finally:
        try:
            os.remove(p)
        except Exception:
            pass
        try:
            os.rmdir(d)
        except Exception:
            pass