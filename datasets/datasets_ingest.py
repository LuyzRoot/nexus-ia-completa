"""
Ingest script: loads files, preprocess, chunk and add to RAGIndex.

Usage (CLI):
python datasets/ingest.py --paths datasets/data/* --namespace my_dataset --chunk-size 1000 --overlap 200

It uses rag.index.RAGIndex and memory.vector_store.get_default_vector_store by default.
"""

import argparse
import asyncio
import logging
from typing import List
import os

from datasets.loader import discover_files, load_jsonl, load_csv
from datasets.preprocess import prepare_document, chunk_text_by_chars
from rag.index import RAGIndex

logger = logging.getLogger("datasets.ingest")
logging.basicConfig(level=logging.INFO)


async def ingest_documents(paths: List[str], namespace: str = None, chunk_size: int = 1000, overlap: int = 200, batch: int = 10):
    # create index (in-memory default)
    idx = RAGIndex()
    files = discover_files(paths, extensions=[".jsonl", ".csv", ".txt", ".md", ".parquet"])
    logger.info("Found %d files to ingest", len(files))
    for fpath in files:
        ext = os.path.splitext(fpath)[1].lower()
        logger.info("Loading %s", fpath)
        if ext == ".jsonl":
            loader = load_jsonl
        elif ext == ".csv":
            loader = load_csv
        elif ext in (".txt", ".md"):
            # wrap simple text file into a single document
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                raw = {"text": fh.read(), "source": fpath}
                doc = prepare_document(raw)
                chunks = chunk_text_by_chars(doc["text"], chunk_size=chunk_size, overlap=overlap)
                docs = []
                for c in chunks:
                    meta = dict(doc["metadata"])
                    meta.update({"source": fpath, "chunk_index": c["index"], "start": c["start"], "end": c["end"]})
                    docs.append({"id": f"{doc['id']}::chunk::{c['index']}", "text": c["text"], "metadata": meta})
                await idx.add_documents(docs)
            continue
        elif ext in (".parquet", ".pq"):
            loader = None  # handled by loader.load_parquet via discover + explicit call if desired
        else:
            logger.info("Skipping unsupported extension %s", ext)
            continue

        if loader:
            docs_batch = []
            for raw in loader(fpath):
                doc = prepare_document(raw)
                chunks = chunk_text_by_chars(doc["text"], chunk_size=chunk_size, overlap=overlap)
                for c in chunks:
                    meta = dict(doc["metadata"])
                    meta.update({"source": fpath, "original_id": doc["id"], "chunk_index": c["index"], "start": c["start"], "end": c["end"]})
                    docs_batch.append({"id": f"{doc['id']}::chunk::{c['index']}", "text": c["text"], "metadata": meta})
                    if len(docs_batch) >= batch:
                        await idx.add_documents(docs_batch)
                        docs_batch = []
            if docs_batch:
                await idx.add_documents(docs_batch)
    logger.info("Ingestion finished")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", required=True, help="Paths or directories to ingest (supports globbing expanded by shell)")
    parser.add_argument("--namespace", type=str, default=None, help="Optional namespace to prefix doc ids")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--overlap", type=int, default=200)
    parser.add_argument("--batch", type=int, default=20)
    args = parser.parse_args()
    # Expand paths that might contain globs / shells usually expand; if not, pass raw list
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ingest_documents(args.paths, namespace=args.namespace, chunk_size=args.chunk_size, overlap=args.overlap, batch=args.batch))


if __name__ == "__main__":
    main()