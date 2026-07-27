# RAG (Retrieval-Augmented Generation)

Componentes principais localizados em `rag/`:
- loader.py — carrega documentos (txt, md, pdf)
- chunker.py — divide texto em chunks com overlap
- index.py — RAGIndex que usa vector store (memory/pgvector/FAISS)
- retriever.py — pipeline de retrieval + opcional rerank
- reranker.py — usa LLM para reordenar candidatos (se disponível)

Fluxo de ingestão
1. Coloque arquivos em `datasets/data/` ou em sua pasta de documentos.
2. Execute:
```bash
python datasets/ingest.py --paths datasets/data/* --namespace meu_dataset