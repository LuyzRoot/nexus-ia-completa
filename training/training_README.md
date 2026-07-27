# NEXUS - Training module

Conteúdo:
- config.py: definições de configuração reutilizáveis.
- utils.py: utilitários (seed, dataset split, logging).
- prepare_data.py: scripts para normalizar e preparar datasets (JSONL/CSV -> HF Dataset).
- fine_tune_lm.py: fine-tune de modelos de linguagem (causal ou seq2seq) via Hugging Face `Trainer`.
- finetune_embeddings.py: treina / afina modelos de embeddings via `sentence-transformers`.
- train_reranker.py: treinamento de reranker (cross-encoder) via `sentence-transformers` CrossEncoder.
- evaluate.py: métricas básicas (ROUGE/BLEU/accuracy/recall@k).
- scripts/: exemplos de scripts shell para rodar treinamentos.
- requirements.txt: dependências recomendadas.
- Dockerfile: imagem Docker para execução.

Como usar (exemplos)
1) Prepare os dados:
   python training/prepare_data.py --input datasets/data/myset.jsonl --out training/data/processed --text-field text --id-field id

2) Treinar LM (exemplo):
   python training/fine_tune_lm.py --train-file training/data/processed/train.jsonl --validation-file training/data/processed/val.jsonl --model-name-or-path gpt2 --output-dir outputs/lm_finetune --per-device-train-batch-size 4 --num-train-epochs 1

3) Treinar embeddings:
   python training/finetune_embeddings.py --train-file training/data/processed/emb_train.tsv --model-name sentence-transformers/all-MiniLM-L6-v2 --output-dir outputs/emb_finetune

4) Treinar reranker:
   python training/train_reranker.py --train-file training/data/processed/rerank_train.tsv --model-name cross-encoder/ms-marco-MiniLM-L-6-v2 --output-dir outputs/reranker

Observações
- Use GPU (CUDA) para treinos pesados.
- Ajuste hyperparams via CLI flags ou criando um arquivo de configuração.
- Para produção, use `accelerate` / distributed training; o código usa Trainer e sentence-transformers API compatíveis.