import pytest

def test_short_term_context_and_prune(setup_test_db):
    mem_mod = pytest.importorskip("memory.short_term")
    # create messages via DB session
    import app.database.session as db_session_mod  # type: ignore
    SessionLocal = db_session_mod.SessionLocal
    s = SessionLocal()
    try:
        # create conversation and messages
        from app.models import User, Conversation, Message  # type: ignore
        user = User(email="mem@example.com", hashed_password="x")
        s.add(user); s.commit(); s.refresh(user)
        conv = Conversation(user_id=user.id, title="c1")
        s.add(conv); s.commit(); s.refresh(conv)
        # add 5 messages
        for i in range(5):
            msg = Message(conversation_id=conv.id, role="user", content=f"m{i}")
            s.add(msg)
        s.commit()

        ctx = mem_mod.get_short_term_context(s, conv.id, max_messages=3)
        assert isinstance(ctx, list)
        assert len(ctx) <= 3
    finally:
        s.close()