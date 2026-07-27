# NEXUS Frontend

Vite + React + TypeScript minimal frontend for NEXUS.

Instalação
1. Entre na pasta frontend:
   cd frontend

2. Instale dependências:
   npm install

3. Rode em modo dev:
   npm run dev

Proxy
- Vite config proxia /api -> http://localhost:8000 e /inference -> http://localhost:8001.
- Ajuste se suas portas/hosts forem diferentes.

O que inclui
- Login (chamada a /api/v1/auth/login)
- Chat com streaming (POST /inference/stream)
- Agents (GET /api/v1/agents, DELETE /api/v1/agents/:id)
- RAG retrieval (POST /inference/retrieve)
- Autenticação simples via token no localStorage

Notas
- Ajuste os endpoints caso sua API esteja em caminhos diferentes.
- Este frontend é um ponto de partida: adapte UI/UX, validações, tratamento de erros e segurança conforme necessário.