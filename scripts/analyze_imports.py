"""Analyze imports across the repository and produce reports.

Usage:
    python scripts/analyze_imports.py --repo-root . --out report.json

This script is read-only and intended to be run locally or in CI to
produce a dependency/import graph and identify candidate orphan files,
duplicate filenames, and simple heuristics for unused definitions.

Limitations: dynamic imports (importlib, __import__, getattr, exec)
may hide usage and cause false positives. Review results manually.
"""

import ast
from pathlib import Path
import json
import argparse
from collections import defaultdict

PY_SUFFIXES = {'.py'}


def iter_python_files(root: Path):
    for p in root.rglob('*.py'):
        # skip virtual envs or hidden dirs
        if any(part.startswith('.') for part in p.parts):
            continue
        yield p


def parse_imports(path: Path):
    imports = []
    try:
        node = ast.parse(path.read_text(encoding='utf-8'))
    except Exception:
        return imports
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.append(alias.name)
        elif isinstance(n, ast.ImportFrom):
            module = n.module or ''
            imports.append(module)
    return imports


def find_definitions(path: Path):
    defs = []
    try:
        node = ast.parse(path.read_text(encoding='utf-8'))
    except Exception:
        return defs
    for n in node.body:
        if isinstance(n, ast.FunctionDef):
            defs.append(('func', n.name))
        elif isinstance(n, ast.AsyncFunctionDef):
            defs.append(('afunc', n.name))
        elif isinstance(n, ast.ClassDef):
            defs.append(('class', n.name))
    return defs


def main(repo_root: str, out: str = None):
    root = Path(repo_root).resolve()
    files = list(iter_python_files(root))

    imports_map = defaultdict(list)
    defined_map = defaultdict(list)
    name_to_files = defaultdict(list)

    for f in files:
        rel = str(f.relative_to(root))
        name_to_files[f.name].append(rel)
        imports = parse_imports(f)
        for imp in imports:
            imports_map[rel].append(imp)
        defs = find_definitions(f)
        for d in defs:
            defined_map[rel].append(d)

    # build reverse map: which files import a module/file (heuristic)
    imported_by = defaultdict(list)
    for f, imps in imports_map.items():
        for imp in imps:
            imported_by[imp].append(f)

    report = {
        'total_python_files': len(files),
        'files': list(name_to_files.items()),
        'duplicates': {n: p for n, p in name_to_files.items() if len(p) > 1},
        'imports_map': imports_map,
        'defined_map': defined_map,
        'imported_by': imported_by,
    }

    if out:
        Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"Wrote report to {out}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', default='.', help='Path to repository root')
    parser.add_argument('--out', default=None, help='Output file (json)')
    args = parser.parse_args()
    main(args.repo_root, args.out)
