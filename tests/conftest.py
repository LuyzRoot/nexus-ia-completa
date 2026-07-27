import os
import tempfile
import importlib
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Try to import the FastAPI app (adjust if your app module differs)
fastapi_app = None
try:
    # common location
    from app.main import app as fastapi_app  # type: ignore
except Exception:
    try:
        # alternative
        from app import main
        fastapi_app = getattr(main, "app", None)
    except Exception:
        fastapi_app = None

if fastapi_app is None:
    # tests will error early, but keep fixtures defined so individual tests can skip
    pass

@pytest.fixture(scope="session")
def event_loop():
    """Provide an asyncio event loop for tests that call asyncio.run-like behavior."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def in_memory_engine():
    """Create a SQLite in-memory engine for the test session."""
    # Using pysqlite memory URL that supports multiple threads for TestClient
    url = "sqlite+pysqlite:///:memory:"
    engine = create_engine(url, connect_args={"check_same_thread": False}, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    return engine, SessionLocal

@pytest.fixture(autouse=True)
def setup_test_db(in_memory_engine, monkeypatch):
    """
    Auto fixture to create/drop all tables from app.models.Base on the test engine.
    Also patches app.database.session.SessionLocal and engine if present.
    """
    engine, SessionLocal = in_memory_engine
    # Import models and create tables
    try:
        import app.models as models  # type: ignore
    except Exception:
        pytest.skip("app.models not importable; skip DB-backed tests")

    models.Base.metadata.create_all(bind=engine)

    # Patch SessionLocal and engine in app.database.session if it exists
    try:
        import app.database.session as db_session_mod  # type: ignore
        monkeypatch.setattr(db_session_mod, "engine", engine, raising=False)
        monkeypatch.setattr(db_session_mod, "SessionLocal", SessionLocal, raising=False)
    except Exception:
        # try package-level
        try:
            import app.database as app_db_pkg  # type: ignore
            monkeypatch.setattr(app_db_pkg, "engine", engine, raising=False)
            monkeypatch.setattr(app_db_pkg, "SessionLocal", SessionLocal, raising=False)
        except Exception:
            pass

    yield

    # teardown
    try:
        models.Base.metadata.drop_all(bind=engine)
    except Exception:
        pass

@pytest.fixture
def client(monkeypatch):
    """FastAPI TestClient with DB dependency override to use test SessionLocal."""
    if fastapi_app is None:
        pytest.skip("FastAPI app not importable (app.main.app). Skipping API tests.")
    # Try to override get_db dependency if present
    try:
        import app.database.session as db_session_mod  # type: ignore
    except Exception:
        db_session_mod = None

    def _get_test_db():
        # create new session from patched SessionLocal
        if db_session_mod is None:
            raise RuntimeError("Test DB session module not available")
        session = db_session_mod.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    # Try to set dependency override if get_db is available
    try:
        import app.database as app_db_pkg  # type: ignore
        get_db = getattr(app_db_pkg, "get_db", None)
        if get_db:
            fastapi_app.dependency_overrides[get_db] = _get_test_db  # type: ignore
    except Exception:
        pass

    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture
def monkeypatch_embeddings(monkeypatch):
    """
    Patch core.embeddings.embed_text to a deterministic async function for tests.
    """
    try:
        import core.embeddings as embed_mod  # type: ignore
    except Exception:
        # if module not present, nothing to patch
        yield
        return

    async def fake_embed(text: str):
        # deterministic vector based on text length (fixed size)
        base = (len(text) % 10) + 1.0
        return [float(base) for _ in range(16)]

    monkeypatch.setattr(embed_mod, "embed_text", fake_embed, raising=False)
    yield

@pytest.fixture
def monkeypatch_llm(monkeypatch):
    """
    Patch core.llm.llm_router.generate and stream_generate with deterministic responses.
    """
    try:
        import core.llm as llm_mod  # type: ignore
    except Exception:
        yield
        return

    class DummyResp:
        def __init__(self, text="ok", provider_name="mock", model="mock-model", tools_used=None):
            self.text = text
            self.provider_name = provider_name
            self.model = model
            self.tools_used = tools_used or []

    async def fake_generate(messages, temperature=None, **kwargs):
        # join user messages
        parts = []
        for m in messages:
            if isinstance(m, dict):
                parts.append(m.get("content", ""))
            else:
                # if messages are strings
                parts.append(str(m))
        text = " ".join([p for p in parts if p])
        return DummyResp(text=f"echo: {text}", provider_name="mock", model="mock")

    async def fake_stream_generate(messages, temperature=None, **kwargs):
        # yield pieces of a dummy response
        content = (await fake_generate(messages)).text
        for i in range(0, len(content), 16):
            yield content[i : i + 16]

    # Monkeypatch on llm_router object if present
    try:
        llm_router = getattr(llm_mod, "llm_router", None)
        if llm_router:
            monkeypatch.setattr(llm_router, "generate", fake_generate, raising=False)
            monkeypatch.setattr(llm_router, "stream_generate", fake_stream_generate, raising=False)
    except Exception:
        # fallback: set functions on module
        monkeypatch.setattr(llm_mod, "generate", fake_generate, raising=False)
        monkeypatch.setattr(llm_mod, "stream_generate", fake_stream_generate, raising=False)

    yield