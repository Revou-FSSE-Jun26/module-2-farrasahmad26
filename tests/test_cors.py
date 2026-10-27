from app import create_app

TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
}


def preflight(app, origin):
    return app.test_client().options('/products', headers={
        'Origin': origin,
        'Access-Control-Request-Method': 'GET',
    })


def test_cors_defaults_to_localhost(monkeypatch):
    monkeypatch.delenv('CORS_ORIGINS', raising=False)
    app = create_app(TEST_CONFIG)

    response = preflight(app, 'http://localhost:3000')
    assert response.headers.get('Access-Control-Allow-Origin') == 'http://localhost:3000'


def test_cors_allows_origins_from_env(monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS', 'http://localhost:3000, https://revocoffee.vercel.app/')
    app = create_app(TEST_CONFIG)

    response = preflight(app, 'https://revocoffee.vercel.app')
    assert response.headers.get('Access-Control-Allow-Origin') == 'https://revocoffee.vercel.app'


def test_cors_blocks_unknown_origin(monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS', 'http://localhost:3000')
    app = create_app(TEST_CONFIG)

    response = preflight(app, 'https://evil.example.com')
    assert 'Access-Control-Allow-Origin' not in response.headers
