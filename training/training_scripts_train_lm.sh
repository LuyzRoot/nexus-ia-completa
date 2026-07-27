#!/usr/bin/env bash
# Example training script (local, single GPU)
TRAIN_FILE="training/data/processed/train.jsonl"
VAL_FILE="training/data/processed/val.jsonl"
MODEL="gpt2"
OUTDIR="outputs/lm_finetune_local"
python training/fine_tune_lm.py --train-file "$TRAIN_FILE" --validation-file "$VAL_FILE" --model-name-or-path "$MODEL" --output-dir "$OUTDIR" --per-device-train-batch-size 2 --num-train-epochs 1