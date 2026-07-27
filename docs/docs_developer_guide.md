# Guia do Desenvolvedor

Padrões, organização de código e boas práticas.

Estrutura de diretórios (resumida)
- app/               — backend FastAPI principal
  - models.py        — ORM SQLAlchemy
  - database/        — engines/session/migrations helpers
  - auth/            — autenticação e dependências
  - api/             — routers e endpoints
- inference/         — microservice de inferência (streaming, RAG)
- rag/               — loader, chunker, index, retriever, reranker
- multimodal/        — imagem, áudio, OCR, pipelines
- tools/             — utilitários (filesystem, browser, search)
- plugins/           — sistema de plugins e exemplos
- training/          — scripts de treinamento e configs
- datasets/          — padrões para datasets e ingestão
- monitoring/        — métricas, middleware, healthchecks
- frontend/          — aplicação web (React + TS)
- tests/             — testes e fixtures

Contribuindo com código
1. Crie uma branch a partir de `main`:
```bash
git checkout -b feat/minha-nova-funcionalidade