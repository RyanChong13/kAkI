"""Test API auth endpoints — register and login."""


def test_register_success(client):
    """Registering a new user returns user data."""
    res = client.post("/auth/register", json={
        "email": "new@test.com",
        "password": "password123",
        "name": "New User",
        "age": 25,
        "sector": "technology",
        "income_band": "medium",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "new@test.com"
    assert data["name"] == "New User"


def test_register_duplicate_email(client):
    """Registering with existing email returns 400."""
    client.post("/auth/register", json={
        "email": "dup@test.com", "password": "pass", "name": "User1",
    })
    res = client.post("/auth/register", json={
        "email": "dup@test.com", "password": "pass", "name": "User2",
    })
    assert res.status_code == 400


def test_login_success(client):
    """Login with valid credentials returns JWT token."""
    client.post("/auth/register", json={
        "email": "login@test.com", "password": "secret", "name": "Login User",
    })
    res = client.post("/auth/login", json={
        "email": "login@test.com", "password": "secret",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Login with wrong password returns 401."""
    client.post("/auth/register", json={
        "email": "bad@test.com", "password": "correct", "name": "Bad User",
    })
    res = client.post("/auth/login", json={
        "email": "bad@test.com", "password": "wrong",
    })
    assert res.status_code == 401
