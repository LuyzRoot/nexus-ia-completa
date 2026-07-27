"""
Dataset validation helpers.

Checks:
- file format correctness (jsonl lines parse)
- minimal required fields present (by default checks 'text' or content fields)
- sample output
"""

import argparse
import json
import logging
from datasets.loader import load_jsonl, load_csv, discover_files

logger = logging.getLogger("datasets.validate")
logging.basicConfig(level=logging.INFO)


def validate_jsonl(path: str, require_text: bool = True, max_errors: int = 10) -> dict:
    errors = []
    count = 0
    for obj in load_jsonl(path):
        count += 1
        if require_text:
            if not any(obj.get(k) for k in ("text", "content", "body", "description")):
                errors.append({"line": count, "error": "missing text-like field"})
                if len(errors) >= max_errors:
                    break
    return {"path": path, "count": count, "errors": errors}


def validate_csv(path: str, require_text: bool = True, max_errors: int = 10) -> dict:
    errors = []
    count = 0
    for obj in load_csv(path):
        count += 1
        if require_text:
            if not any(obj.get(k) for k in ("text", "content", "body", "description")):
                errors.append({"row": count, "error": "missing text-like field"})
                if len(errors) >= max_errors:
                    break
    return {"path": path, "count": count, "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="file(s) or directories to validate")
    args = parser.parse_args()
    files = discover_files(args.paths, extensions=[".jsonl", ".csv", ".txt", ".md"])
    summary = {"checked": [], "failures": []}
    for f in files:
        if f.lower().endswith(".jsonl"):
            r = validate_jsonl(f)
        elif f.lower().endswith(".csv"):
            r = validate_csv(f)
        else:
            # simple check for text files
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read(200)
                    r = {"path": f, "count": 1, "errors": [] if content else [{"error": "empty file"}]}
            except Exception as exc:
                r = {"path": f, "count": 0, "errors": [{"error": str(exc)}]}
        summary["checked"].append(r)
        if r.get("errors"):
            summary["failures"].append(r)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()