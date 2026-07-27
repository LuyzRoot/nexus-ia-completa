#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Wrapper para training/fine_tune_lm.py
ENV_FILE=".env"
TRAIN_FILE="training/data/processed/train.jsonl"
VAL_FILE="training/data/processed/val.jsonl"
MODEL="gpt2"
OUTDIR="outputs/lm_finetune"
BATCH=4
EPOCHS=1
FP16=0

usage(){
  cat <<EOF
train_lm.sh - Treinar modelo de linguagem (wrapper)

Usage:
  ./scripts/train_lm.sh [--train TRAIN_FILE] [--val VAL_FILE] [--model MODEL] [--out OUTDIR] [--batch N] [--epochs E] [--fp16]

Options:
  --train PATH
  --val PATH
  --model MODEL
  --out DIR
  --batch N
  --epochs E
  --fp16
EOF
}

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

# simple parse
while [[ $# -gt 0 ]]; do
  case "$1" in
    --train) shift; TRAIN_FILE="$1"; shift;;
    --val) shift; VAL_FILE="$1"; shift;;
    --model) shift; MODEL="$1"; shift;;
    --out) shift; OUTDIR="$1"; shift;;
    --batch) shift; BATCH="$1"; shift;;
    --epochs) shift; EPOCHS="$1"; shift;;
    --fp16) FP16=1; shift;;
    --help|-h) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

CMD=(python training/fine_tune_lm.py --train-file "$TRAIN_FILE" --validation-file "$VAL_FILE" --model-name-or-path "$MODEL" --output-dir "$OUTDIR" --per-device-train-batch-size "$BATCH" --num-train-epochs "$EPOCHS")
if [[ "$FP16" -eq 1 ]]; then
  CMD+=(--fp16)
fi

echo "Running: ${CMD[*]}"
"${CMD[@]}"