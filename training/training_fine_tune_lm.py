"""
Fine-tune a language model (causal or encoder-decoder) using Hugging Face Trainer.
Supports loading JSONL files where each line is {"id":..., "text": "..."}.

Usage example:
python training/fine_tune_lm.py --train-file training/data/processed/train.jsonl --validation-file training/data/processed/val.jsonl --model-name-or-path gpt2 --output-dir outputs/lm_finetune --per-device-train-batch-size 2 --num-train-epochs 1
"""
import argparse
import os
import logging
from typing import Optional
import json

from datasets import load_dataset
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, DataCollatorForLanguageModeling, Trainer, TrainingArguments
from training.config import LMTrainingConfig
from training.utils import set_seed, ensure_dir

logger = logging.getLogger("training.fine_tune_lm")
logging.basicConfig(level=logging.INFO)


def is_encoder_decoder(model_name_or_path: str) -> bool:
    # naive detection by model type string
    lower = model_name_or_path.lower()
    return any(k in lower for k in ["t5", "flan", "gpt-neo-x-20b"]) and "gpt" not in lower


def load_dataset_from_jsonl(train_file: str, validation_file: Optional[str] = None):
    data_files = {"train": train_file}
    if validation_file:
        data_files["validation"] = validation_file
    dataset = load_dataset("json", data_files=data_files)
    return dataset


def preprocess_function(examples, tokenizer, max_length):
    texts = examples["text"]
    # tokenization
    return tokenizer(texts, truncation=True, max_length=max_length, padding="max_length")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file", required=True)
    parser.add_argument("--validation-file", required=False)
    parser.add_argument("--model-name-or-path", default="gpt2")
    parser.add_argument("--output-dir", default="outputs/lm_finetune")
    parser.add_argument("--per-device-train-batch-size", type=int, default=4)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=4)
    parser.add_argument("--num-train-epochs", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--max-seq-length", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fp16", action="store_true")
    args = parser.parse_args()

    set_seed(args.seed)
    ensure_dir(args.output_dir)

    encoder_decoder = is_encoder_decoder(args.model_name_or_path)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=True)
    # pad token handling for causal models
    if not encoder_decoder and tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    # model selection
    try:
        if encoder_decoder:
            model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name_or_path)
        else:
            model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path)
    except Exception as exc:
        logger.exception("Failed to load model: %s", exc)
        raise

    dataset = load_dataset_from_jsonl(args.train_file, args.validation_file)
    tokenized = dataset.map(lambda ex: preprocess_function(ex, tokenizer, args.max_seq_length), batched=True, remove_columns=dataset["train"].column_names)

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False) if not encoder_decoder else DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        logging_steps=100,
        save_strategy="steps",
        save_steps=500,
        fp16=args.fp16,
        evaluation_strategy="steps" if args.validation_file else "no",
        eval_steps=500 if args.validation_file else None,
        seed=args.seed,
        push_to_hub=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"] if "validation" in tokenized else None,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    logger.info("Training finished and saved to %s", args.output_dir)


if __name__ == "__main__":
    main()