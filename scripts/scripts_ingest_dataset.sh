#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Wrapper para datasets/ingest.py
ENV_FILE=".env"
CHUNK_SIZE=1000
OVERLAP=200
BATCH=20
NAMESPACE="default"

usage(){
  cat <<EOF
ingest_dataset.sh - Ingesta de documentos para RAG index

Usage:
  ./scripts/ingest_dataset.sh --paths "datasets/data/*" [--namespace ns] [--chunk-size N] [--overlap M] [--batch B]

Options:
  --paths PATHS     (obrigatório) paths ou glob para arquivos a serem ingeridos
  --namespace NAME  namespace opcional para doc ids
  --chunk-size N
  --overlap M
  --batch B
EOF
}

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

if [[ $# -lt 1 ]]; then
  echo "Use --paths to provide input files"
fi

# parse simple args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --paths) shift; PATHS="$1"; shift;;
    --namespace) shift; NAMESPACE="$1"; shift;;
    --chunk-size) shift; CHUNK_SIZE="$1"; shift;;
    --overlap) shift; OVERLAP="$1"; shift;;
    --batch) shift; BATCH="$1"; shift;;
    --help|-h) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ -z "${PATHS:-}" ]]; then
  echo "Error: --paths is required"; usage; exit 1
fi

echo "Ingesting files: $PATHS namespace=$NAMESPACE chunk=$CHUNK_SIZE overlap=$OVERLAP batch=$BATCH"
python datasets/ingest.py --paths $PATHS --namespace "$NAMESPACE" --chunk-size "$CHUNK_SIZE" --overlap "$OVERLAP" --batch "$BATCH"