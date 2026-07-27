# evaluation

Ferramentas para avaliar componentes do NEXUS:

- generation: métricas para modelos de geração (ROUGE, BLEU, sacrebleu, bert-score quando disponível).
- retriever: métricas para recuperação de documentos (recall@k, MRR, precision@k, NDCG).
- reranker: avaliação de rerankers (MRR / accuracy over labeled pairs).
- benchmarks: scripts para rodar experimentos e comparar modelos/strategies.
- visualize: plot helpers para visualizar resultados.

Principais scripts:
- evaluation/eval_generation.py  -> avalia outputs gerados vs referências (JSONL input)
- evaluation/eval_retriever.py   -> avalia retriever results (JSONL with positives)
- evaluation/benchmarks.py      -> runs comparisons and exports CSV summary
- evaluation/cli.py             -> CLI wrapper for evaluation tasks
- evaluation/visualize.py       -> plotting helpers

Formato de entrada (geração)
- JSONL file where each line: {"id": "<id>", "prediction": "<text>", "reference": "<text>"}
  or two files: predictions.jsonl and references.jsonl with matching ids.

Formato de entrada (retriever)
- JSONL where each line: {"query":"...", "positive_ids":["id1","id2"], "retrieved":["idA","idB",...]}

Requisitos (opcionais)
- pip install evaluate sacrebleu rouge_score bert-score scikit-learn matplotlib seaborn pandas

Uso rápido
- python evaluation/eval_generation.py --pred predictions.jsonl --refs references.jsonl --out results.json
- python evaluation/eval_retriever.py --file retriever_results.jsonl --k 10 --out retriever_metrics.json