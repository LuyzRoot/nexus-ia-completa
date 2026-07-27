# NEXUS IA v2.0 - Setup Rápido

## 1. Configurar .env
```bash
cp .env.example .env
```
Edite com suas chaves:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=seu-secret-aqui
```

## 2. Infraestrutura
```bash
docker-compose up -d postgres redis
```

## 3. Dependências
```bash
pip install -r requirements.txt
```

## 4. Database
```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## 5. Rodar
```bash
python -m uvicorn app.main:app --reload
```

Acesse: **http://localhost:8000/docs**

---

## ✅ Estrutura v2.0 Pronta

- `app/main.py` - FastAPI v2.0
- `core/config.py` - Settings
- `core/llm/router.py` - LLM Router com fallback
- `models/` - ORM completo
- `api/auth/` - Auth JWT
- `api/chat/` - Chat routes
- `database/session.py` - SQLAlchemy async
- `core/memory/manager.py` - Redis
- `tests/test_api.py` - Testes básicos
