import pytest

def test_models_crud(setup_test_db):
    """Simple CRUD smoke test for core models (User, Conversation, Message, MemoryEntry)."""
    try:
        from app.models import User, Conversation, Message, MemoryEntry  # type: ignore
    except Exception:
        pytest.skip("app.models not available")

    # Use a fresh Session from app.database.session.SessionLocal
    try:
        import app.database.session as db_session_mod  # type: ignore
        SessionLocal = getattr(db_session_mod, "SessionLocal")
    except Exception:
        pytest.skip("app.database.session.SessionLocal not available")

    s = SessionLocal()
    try:
        # Create user
        u = User(email="test@example.com", hashed_password="hashed", full_name="Tester")
        s.add(u)
        s.commit()
        s.refresh(u)
        assert u.id is not None

        # Conversation
        c = Conversation(user_id=u.id, title="conv1")
        s.add(c)
        s.commit()
        s.refresh(c)
        assert c.id is not None

        # Message
        m = Message(conversation_id=c.id, role="user", content="Hello")
        s.add(m)
        s.commit()
        s.refresh(m)
        assert "Hello" in m.content

        # MemoryEntry
        mem = MemoryEntry(user_id=u.id, key="pref", value="blue")
        s.add(mem)
        s.commit()
        s.refresh(mem)
        assert mem.key == "pref"
    finally:
        s.close()