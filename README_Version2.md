# NEXUS SYSTEM AI — Backend (MVP funcional)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](#requirements)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)](#status)

Resumo
------
NEXUS é um backend funcional para assistentes baseados em LLMs — um MVP pronto para desenvolvimento e testes. O objetivo aqui é entregar um núcleo produtivo, simples de rodar em uma VM ou container, com funcionalidades reais de orquestração de modelos, skills (ferramentas), persistência de conversas e integrações multimodais básicas.

Principais funcionalidades implementadas
---------------------------------------
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

Status
------
Este repositório implementa um MVP bem funcional. Algumas características de produção foram deliberadamente deixadas de fora (migrações automáticas produzidas por Alembic, MLOps avançado, orquestração com Kubernetes etc.) e estão listadas na seção "Evolução". O foco foi entregar algo que você possa rodar, testar e estender rapidamente.

Requisitos
----------
- Python 3.10+
- Docker & Docker Compose (recomendado para dev local)
- Node.js 16+ (opcional, para frontend)
- Postgres (se rodar sem Docker)
- Requerimentos Python: `requirements.txt` (ou use os arquivos segmentados para ML/multimodal/dev)

Quickstart (Docker)
-------------------
1. Copie o exemplo de variáveis de ambiente e preencha segredos:
```bash
cp .env.example .env
# edite .env (JWT_SECRET_KEY, chaves de provedores, etc.)