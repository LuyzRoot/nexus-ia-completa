"""
Train a cross-encoder reranker using sentence-transformers CrossEncoder.

Expected training TSV: query \t positive_doc \t negative_doc  (or use pairs with labels)
This script is for small rerankers (cross-encoder).
"""
import argparse
import logging
import os
from sentence_transformers import CrossEncoder
from sentence_transformers.readers import InputExample
import csv
from training.utils import set_seed, ensure_dir

logger = logging.getLogger("training.train_reranker")
logging.basicConfig(level=logging.INFO)


def read_tsv_rerank(path: str):
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) >= 3:
                q, pos, neg = row[0], row[1], row[2]
                examples.append(InputExample(texts=[q, pos], label=1.0))
                examples.append(InputExample(texts=[q, neg], label=0.0))
    return examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file", required=True, help="TSV query<TAB>pos<TAB>neg")
    parser.add_argument("--model-name", default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    parser.add_argument("--output-dir", default="outputs/reranker")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    ensure_dir(args.output_dir)

    examples = read_tsv_rerank(args.train_file)
    if not examples:
        raise RuntimeError("No training examples")

    model = CrossEncoder(args.model_name)
    logger.info("Training reranker with %d examples", len(examples))
    model.fit(train_dataloader=None,  # CrossEncoder.fit expects a DataLoader but has flexible API; we will use its helper
              train_examples=examples,
              epochs=args.epochs,
              batch_size=args.batch_size,
              evaluation_steps=0,
              output_path=args.output_dir)
    logger.info("Reranker saved to %s", args.output_dir)


if __name__ == "__main__":
    main()