# inference

Inference microservice for NEXUS.

Conteúdo:
- server.py         — FastAPI app entrypoint (inclui roteador).
- routes.py         — Endpoints HTTP para inferência (sync, stream, retrieval, batch).
- predictor.py      — Abstração que usa core.llm.llm_router e opcionalmente RAG retriever.
- sse.py            — Helpers para streaming SSE (Server-Sent Events).
- client.py         — Pequeno cliente sync/async para consumir os endpoints.
- utils.py          — Validações e utilitários (token counting, payload checks).
- requirements.txt  — dependências recomendadas.

Principais endpoints
- POST /inference
  - body: { "messages": [{"role":"user","content":"..."}, ...], "temperature": 0.2 }
  - resposta: { "text": "...", "provider": "openai", "model": "gpt-4o-mini" }

- POST /inference/stream
  - SSE stream streaming partial chunks as they arrive.

- POST /inference/retrieve
  - body: { "query": "...", "top_k": 5 }
  - usa RAG retriever se estiver disponível e retorna retrieved passages + generated answer.

- POST /inference/batch
  - body: { "requests": [ {messages...}, ... ] }
  - processa múltiplas requisições em série (método simples de batch).

Execução local (dev)
- uvicorn inference.server:app --reload --port 8001

Observações
- O serviço usa core.llm.llm_router (criado no core/) para chamadas ao LLM.
- Se você habilitar RAG (rag/) o endpoint /inference/retrieve tentará usar rag.retriever.Retriever.
- SSE é implementado via StreamingResponse com formatação text/event-stream.
- Proteja estes endpoints com autenticação + rate-limit em produção.