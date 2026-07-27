# datasets

Estrutura padrão para datasets usados pelo NEXUS RAG / indexação.

Padrão de diretórios:
- datasets/
  - sample/                -> exemplos mínimos (sample.jsonl, sample.csv)
  - data/                  -> local para dados brutos (não comitar dados sensíveis)
  - processed/             -> arquivos gerados (chunks, cleaned)
  - scripts/               -> utilitários (download, s3 helpers)
  - loader.py              -> funções para carregar arquivos (jsonl/csv/parquet)
  - preprocess.py          -> limpeza e chunking de texto
  - ingest.py              -> script/CLI para adicionar ao RAG index
  - validate.py            -> validação e checagem do dataset
  - manifest.json          -> metadados do dataset
  - tests/                 -> testes básicos

Instruções rápidas
1. Ajuste `datasets/manifest.json` com metadados do dataset.
2. Coloque seus dados em `datasets/data/`.
3. Execute:
   - `python datasets/ingest.py --paths datasets/data/* --namespace my_dataset`
   Isso irá chunkar e indexar os documentos no RAGIndex em memória (ou backend configurado).
4. Para validar um dataset:
   - `python datasets/validate.py datasets/sample/sample.jsonl`

Segurança e observabilidade
- Não coloque dados sensíveis no repositório.
- Em produção, use um vector store persistente (pgvector/FAISS) e revise ingest.py para lidar com limites de taxa do provedor de embeddings.