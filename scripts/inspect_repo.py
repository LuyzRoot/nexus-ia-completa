"""Utility to inspect the repository and produce a small report.
This is intentionally non-destructive.
"""
from pathlib import Path
from collections import defaultdict
import json

ROOT = Path(__file__).resolve().parents[1]

def find_duplicate_filenames(root: Path = ROOT):
    files = list(root.rglob('*'))
    name_map = defaultdict(list)
    for f in files:
        if f.is_file():
            name_map[f.name].append(str(f))
    dup = {name: paths for name, paths in name_map.items() if len(paths) > 1}
    return dup

if __name__ == '__main__':
    dup = find_duplicate_filenames()
    print(json.dumps(dup, indent=2))
