"""
Fine-tune a sentence-transformers model for embeddings.

Expected training file format: TSV (anchor \t positive \t [negative]) or huggingface dataset with 'text' fields.
This script uses sentence-transformers' API (InputExample, losses).
"""
import argparse
import logging
import os
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import csv

from training.config import EmbeddingTrainingConfig
from training.utils import set_seed, ensure_dir

logger = logging.getLogger("training.finetune_embeddings")
logging.basicConfig(level=logging.INFO)


def read_tsv_pairs(path: str):
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) >= 2:
                anchor, pos = row[0], row[1]
                examples.append(InputExample(texts=[anchor, pos]))
    return examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file", required=True, help="TSV with anchor<TAB>positive per line")
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--output-dir", default="outputs/emb_finetune")
    parser.add_argument("--train-batch-size", type=int, default=32)
    parser.add_argument("--num-epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    ensure_dir(args.output_dir)

    model = SentenceTransformer(args.model_name)
    train_examples = read_tsv_pairs(args.train_file)
    if not train_examples:
        raise RuntimeError("No training examples found")

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=args.train_batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=args.num_epochs, warmup_steps=100, output_path=args.output_dir)
    logger.info("Embeddings model saved to %s", args.output_dir)


if __name__ == "__main__":
    main()