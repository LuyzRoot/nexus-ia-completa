import pytest

def test_register_login_me(client):
    """Test register, login and /me endpoints if auth router exists."""
    # If auth routes are absent, skip
    try:
        import app.auth.routes  # type: ignore
    except Exception:
        pytest.skip("auth routes not present")

    # Register
    resp = client.post("/api/v1/auth/register", json={"email":"a@example.com","password":"pass","full_name":"A"})
    assert resp.status_code in (201, 200), f"register failed: {resp.status_code} {resp.text}"

    # Login using OAuth2 form data (username, password)
    resp = client.post("/api/v1/auth/login", data={"username":"a@example.com","password":"pass"})
    assert resp.status_code == 200, f"login failed: {resp.status_code} {resp.text}"
    token = resp.json().get("access_token") or resp.json().get("token")
    assert token

    # Use token to call /me
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("email") == "a@example.com"