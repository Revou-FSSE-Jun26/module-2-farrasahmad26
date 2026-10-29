from datetime import datetime
import pytest
from flask_jwt_extended import create_access_token
from configuration.extensions import db
from model.models import User


def token_for(app, email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        token = create_access_token(identity=str(user.id), additional_claims={'email': user.email, 'role': user.role})
        return user.id, {'Authorization': f'Bearer {token}'}


def make_user(app, username, role='user', password='password123'):
    with app.app_context():
        user = User(username=username, email=f'{username}@email.com', role=role, is_active=True, created_at=datetime.now())
        user.hashing_password(password)
        db.session.add(user)
        db.session.commit()
        return user.id


def register(client, username, **extra):
    return client.post('/users', json={'username': username, 'email': f'{username}@email.com', 'password': 'password123', **extra})


# ---- Registration ----

def test_register_is_public_and_role_is_forced_to_user(client):
    response = register(client, 'sneaky', role='admin')
    assert response.status_code == 201
    assert response.get_json()['role'] == 'user'


def test_admin_can_create_admin(client, admin_headers):
    response = client.post('/users', json={'username': 'newadmin', 'email': 'newadmin@email.com', 'password': 'password123', 'role': 'admin'}, headers=admin_headers)
    assert response.status_code == 201
    assert response.get_json()['role'] == 'admin'


def test_register_duplicate_email_or_username_is_case_insensitive(client):
    assert register(client, 'dupe').status_code == 201
    assert client.post('/users', json={'username': 'other', 'email': 'DUPE@email.com', 'password': 'password123'}).status_code == 409
    assert client.post('/users', json={'username': 'DUPE', 'email': 'x@email.com', 'password': 'password123'}).status_code == 409


# ---- Access control ----

@pytest.mark.parametrize('method,path', [
    ('get', '/users'),
    ('get', '/users/1'),
    ('put', '/users/1'),
    ('delete', '/users/1'),
    ('put', '/users/restore/1'),
])
def test_user_management_is_admin_only(client, user_headers, method, path):
    assert getattr(client, method)(path, json={'username': 'x'}).status_code == 401
    assert getattr(client, method)(path, json={'username': 'x'}, headers=user_headers).status_code == 403


def test_admin_lists_users_without_password_hash(client, admin_headers):
    users = client.get('/users', headers=admin_headers).get_json()
    assert users and all('password_hash' not in u for u in users)


# ---- Updates ----

def test_admin_updates_user_and_resets_password(client, app, admin_headers):
    uid = make_user(app, 'editme')
    response = client.put(f'/users/{uid}', json={'username': 'edited', 'role': 'admin', 'password': 'brandnewpass'}, headers=admin_headers)
    assert response.status_code == 200
    assert response.get_json()['username'] == 'edited'
    assert response.get_json()['role'] == 'admin'
    assert client.post('/auth/login', json={'email': 'editme@email.com', 'password': 'brandnewpass'}).status_code == 200


def test_update_rejects_taken_email(client, app, admin_headers):
    uid = make_user(app, 'clash')
    make_user(app, 'taken')
    assert client.put(f'/users/{uid}', json={'email': 'TAKEN@email.com'}, headers=admin_headers).status_code == 409


def test_admin_cannot_demote_or_deactivate_self(client, app, admin_headers):
    with app.app_context():
        admin_id = User.query.filter_by(email='fixture-admin@email.com').first().id
    assert client.put(f'/users/{admin_id}', json={'role': 'user'}, headers=admin_headers).status_code == 400
    assert client.delete(f'/users/{admin_id}', headers=admin_headers).status_code == 400


# ---- Deactivate / restore ----

def test_deactivated_user_cannot_log_in_or_use_old_token(client, app, admin_headers):
    uid = make_user(app, 'banned')
    _, banned = token_for(app, 'banned@email.com')
    assert client.get('/orders', headers=banned).status_code in (200, 404)

    assert client.delete(f'/users/{uid}', headers=admin_headers).status_code == 200

    login = client.post('/auth/login', json={'email': 'banned@email.com', 'password': 'password123'})
    assert login.status_code == 403
    # Wrong password still looks like a normal failed login.
    assert client.post('/auth/login', json={'email': 'banned@email.com', 'password': 'nope12345'}).status_code == 401
    # Token issued before deactivation is rejected.
    assert client.get('/orders', headers=banned).status_code == 401
    # Re-registering with the same email does not bring the account back.
    assert register(client, 'banned').status_code == 409

    listed = client.get('/users?include_inactive=true', headers=admin_headers).get_json()
    assert next(u for u in listed if u['id'] == uid)['is_active'] is False
    assert uid not in [u['id'] for u in client.get('/users', headers=admin_headers).get_json()]
    assert client.get(f'/users/{uid}', headers=admin_headers).status_code == 404
    assert client.get(f'/users/{uid}?include_inactive=true', headers=admin_headers).status_code == 200

    restored = client.put(f'/users/restore/{uid}', headers=admin_headers)
    assert restored.status_code == 200
    assert restored.get_json()['user']['is_active'] is True
    assert client.post('/auth/login', json={'email': 'banned@email.com', 'password': 'password123'}).status_code == 200


def test_role_change_invalidates_old_token(client, app, admin_headers):
    uid = make_user(app, 'promoted')
    _, old = token_for(app, 'promoted@email.com')
    client.put(f'/users/{uid}', json={'role': 'admin'}, headers=admin_headers)
    # Old token still says role=user, so it must be refreshed by logging in again.
    assert client.get('/orders', headers=old).status_code == 401
