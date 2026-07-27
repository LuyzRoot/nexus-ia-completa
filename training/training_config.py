from pydantic import BaseModel
from typing import Optional, List

class LMTrainingConfig(BaseModel):
    model_name_or_path: str = "gpt2"
    output_dir: str = "outputs/lm_finetune"
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 1
    num_train_epochs: int = 1
    learning_rate: float = 5e-5
    weight_decay: float = 0.0
    warmup_steps: int = 0
    logging_steps: int = 100
    save_steps: int = 500
    fp16: bool = False
    seed: int = 42
    max_seq_length: int = 512

class EmbeddingTrainingConfig(BaseModel):
    model_name_or_path: str = "sentence-transformers/all-MiniLM-L6-v2"
    output_dir: str = "outputs/emb_finetune"
    train_batch_size: int = 32
    num_epochs: int = 1
    learning_rate: float = 2e-5
    seed: int = 42

class RerankerTrainingConfig(BaseModel):
    model_name_or_path: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    output_dir: str = "outputs/reranker"
    train_batch_size: int = 16
    num_epochs: int = 1
    learning_rate: float = 2e-5
    seed: int = 42