# NEXUS SYSTEM AI — Backend (MVP funcional)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](#requirements)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)](#status)

## Resumo

NEXUS é um backend funcional para assistentes baseados em LLMs — um MVP pronto para desenvolvimento e testes. O objetivo aqui é entregar um núcleo produtivo, simples de rodar em uma VM ou container.

## Principais funcionalidades implementadas

- Autenticação: registro, login com JWT, hashing com bcrypt.
- RBAC: papéis `user` e `admin`.
- Conversas e mensagens persistidas no Postgres.
- Orquestrador de modelos (Model Router) com fallback entre provedores configuráveis (Anthropic → OpenAI → Gemini → Mock).
- Multi-agentes: perfis de agente (ex.: Executive, Research, Coding) com prompts distintos.
- Memória:
  - Curto prazo: histórico de conversa.
  - Longo prazo: armazenamento key/value por usuário.
- Auditoria: logs de login/registro.
- Streaming SSE para endpoints de chat.
- Voice Engine (ElevenLabs) para TTS e integração com serviços de STT.
- Rate limiting básico nas rotas de chat.
- Skills (ferramentas) integradas e extensíveis.
- Testes automatizados com pytest (SQLite in-memory para isolação).

## Status

Este repositório implementa um MVP bem funcional. Algumas características de produção foram deliberadamente deixadas de fora (migrações automáticas produzidas por Alembic, MLOps avançado, etc.).

## Requisitos

- Python 3.10+
- Docker & Docker Compose (recomendado para dev local)
- Node.js 16+ (opcional, para frontend)
- Postgres (se rodar sem Docker)
- Requerimentos Python: `requirements.txt` (ou use os arquivos segmentados para ML/multimodal/dev)

## Quickstart (Docker)

1. Copie o exemplo de variáveis de ambiente e preencha segredos:
```bash
cp .env.example .env
# edite .env (JWT_SECRET_KEY, chaves de provedores, etc.)
```

2. Inicie os serviços:
```bash
docker-compose -f docker-compose_Version2.yml up -d
```

3. Verifique a saúde:
```bash
curl http://localhost:8000/health
```

## Estrutura do Projeto

```
app/                    Aplicação FastAPI principal
api/                    Schemas e rotas (auth, chat, memory, etc.)
core/                   Lógica de negócio (LLM, agentes, executor)
database/               Camada de persistência (SQLAlchemy)
models/                 Modelos ORM (User, Conversation, Message, etc.)
inference/              Serviço de inferência (opcional)
tests/                  Testes automatizados
monitoring/             Prometheus + Grafana
```

## Como Rodar Localmente (sem Docker)

```bash
# 1. Crie um virtual environment
python -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API

# 4. Inicie a aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testes

```bash
pytest tests/ -v
```

## Endpoints Principais

- `POST /auth/register` - Registrar novo usuário
- `POST /auth/login` - Login e obter token JWT
- `GET /conversations` - Listar conversas
- `POST /chat` - Enviar mensagem (com SSE streaming)
- `GET /memory/{key}` - Recuperar memória de longo prazo
- `POST /voice/tts` - Conversão de texto para fala

## Variáveis de Ambiente

Veja `.env.example` para referência completa. Principais:

- `DATABASE_URL` - Conexão Postgres
- `JWT_SECRET_KEY` - Chave para assinar tokens JWT
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` - Chaves de provedores
- `ELEVENLABS_API_KEY` - Para TTS
- `DEEPGRAM_API_KEY` - Para STT (opcional)

## Licença

MIT

## Branch fix/cleanup-and-skills
Inclui melhorias de segurança, Docker, requirements split, CI e um framework inicial de skills.
