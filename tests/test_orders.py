from datetime import datetime
import pytest
from flask_jwt_extended import create_access_token
from configuration.extensions import db
from model.models import User, Product

CHECKOUT = {
    'first_name': 'Farras',
    'last_name': 'Ahmad',
    'phone': '081234567890',
    'address': 'Jl. Kopi No. 1',
    'city': 'Jakarta Selatan',
    'province': 'DKI Jakarta',
    'postal_code': '12345',
    'country': 'Indonesia',
    'shipping_method': 'fast',
    'payment_method': 'qris',
    'note': 'Please wrap it',
}


@pytest.fixture(scope='module')
def users(app):
    """Creates a second customer and an admin, returns {name: (id, auth headers)}."""
    with app.app_context():
        jane = User(username='Jane', email='jane@email.com', role='user', is_active=True, created_at=datetime.now())
        jane.hashing_password('password123')
        admin = User(username='Admin', email='admin@email.com', role='admin', is_active=True, created_at=datetime.now())
        admin.hashing_password('password123')
        db.session.add_all([jane, admin])
        db.session.commit()
        john = User.query.filter_by(email='johntest123@email.com').first()

        def auth(user):
            token = create_access_token(identity=str(user.id), additional_claims={'email': user.email, 'role': user.role})
            return user.id, {'Authorization': f'Bearer {token}'}

        return {'john': auth(john), 'jane': auth(jane), 'admin': auth(admin)}


@pytest.fixture(scope='module')
def product_ids(app):
    with app.app_context():
        return {p.slug: p.id for p in Product.query.all()}


def create(client, headers, product_ids, **extra):
    body = {'items': [{'product_id': product_ids['webcam'], 'quantity': 1}], **CHECKOUT, **extra}
    return client.post('/orders', json=body, headers=headers)


def test_orders_require_login(client):
    assert client.get('/orders').status_code == 401
    assert client.get('/orders/1').status_code == 401
    assert client.post('/orders', json={'items': [{'product_id': 1, 'quantity': 1}]}).status_code == 401
    assert client.put('/orders/1', json={'status': 'cancelled'}).status_code == 401


def test_create_order_saves_checkout_details_and_uses_token_user(client, users, product_ids):
    jane_id, jane = users['jane']
    john_id, _ = users['john']
    # user_id in the body is ignored: the order belongs to whoever owns the token.
    response = create(client, jane, product_ids, user_id=john_id, status='completed')
    assert response.status_code == 201
    data = response.get_json()
    assert data['user_id'] == jane_id
    assert data['status'] == 'pending'
    assert data['first_name'] == 'Farras'
    assert data['province'] == 'DKI Jakarta'
    assert data['payment_method'] == 'qris'
    assert data['note'] == 'Please wrap it'
    assert data['email'] == 'jane@email.com'
    assert data['items'][0]['name'] == 'Webcam'
    assert data['items'][0]['category'] == 'Electronics'


def test_shipping_cost_is_calculated_by_backend(client, users, product_ids):
    _, jane = users['jane']
    # Webcam is $99.99: fast = $15, regular is free over $50, cargo = $8.
    fast = create(client, jane, product_ids, shipping_method='fast', shipping_cost=0).get_json()
    assert fast['shipping_cost'] == 15.0
    assert fast['total_price'] == pytest.approx(114.99)

    regular = create(client, jane, product_ids, shipping_method='regular').get_json()
    assert regular['shipping_cost'] == 0.0
    assert regular['total_price'] == pytest.approx(99.99)

    cargo = create(client, jane, product_ids, shipping_method='cargo').get_json()
    assert cargo['shipping_cost'] == 8.0


def test_create_order_without_checkout_details_still_works(client, users, product_ids):
    _, jane = users['jane']
    response = client.post('/orders', json={'items': [{'product_id': product_ids['webcam'], 'quantity': 2}]}, headers=jane)
    assert response.status_code == 201
    assert response.get_json()['shipping_cost'] == 0.0
    assert response.get_json()['first_name'] is None


@pytest.mark.parametrize('field,value,code', [
    ('shipping_method', 'teleport', 400),
    ('payment_method', 'cash', 400),
    ('postal_code', '123', 422),
    ('phone', '12345', 422),
    ('first_name', 123, 400),
    ('note', 'x' * 501, 422),
])
def test_create_order_invalid_checkout_field(client, users, product_ids, field, value, code):
    _, jane = users['jane']
    assert create(client, jane, product_ids, **{field: value}).status_code == code


def test_customers_only_see_their_own_orders(client, users, product_ids):
    jane_id, jane = users['jane']
    _, john = users['john']
    jane_order = create(client, jane, product_ids).get_json()

    listed = client.get('/orders', headers=jane).get_json()
    assert listed and all(o['user_id'] == jane_id for o in listed)

    # John can't read Jane's order (404, not 403, so its existence isn't leaked).
    assert client.get(f"/orders/{jane_order['id']}", headers=john).status_code == 404
    assert client.get(f"/orders/{jane_order['id']}", headers=jane).status_code == 200


def test_admin_sees_all_orders(client, users, product_ids):
    _, admin = users['admin']
    owners = {o['user_id'] for o in client.get('/orders', headers=admin).get_json()}
    assert users['jane'][0] in owners and users['john'][0] in owners


def test_customer_can_cancel_own_pending_order(client, users, product_ids):
    _, jane = users['jane']
    order = create(client, jane, product_ids).get_json()
    response = client.put(f"/orders/{order['id']}", json={'status': 'cancelled'}, headers=jane)
    assert response.status_code == 200
    assert response.get_json()['status'] == 'cancelled'
    # Already cancelled orders can't change again.
    assert client.put(f"/orders/{order['id']}", json={'status': 'cancelled'}, headers=jane).status_code == 400


def test_customer_cannot_cancel_someone_elses_order(client, users, product_ids):
    _, jane = users['jane']
    _, john = users['john']
    order = create(client, jane, product_ids).get_json()
    assert client.put(f"/orders/{order['id']}", json={'status': 'cancelled'}, headers=john).status_code == 404
    assert client.get(f"/orders/{order['id']}", headers=jane).get_json()['status'] == 'pending'


def test_only_admin_can_complete_an_order(client, users, product_ids):
    _, jane = users['jane']
    _, admin = users['admin']
    order = create(client, jane, product_ids).get_json()
    assert client.put(f"/orders/{order['id']}", json={'status': 'completed'}, headers=jane).status_code == 403
    response = client.put(f"/orders/{order['id']}", json={'status': 'completed'}, headers=admin)
    assert response.status_code == 200
    assert response.get_json()['status'] == 'completed'


def test_delete_order_is_admin_only(client, users, product_ids):
    _, jane = users['jane']
    _, admin = users['admin']
    order = create(client, jane, product_ids).get_json()
    assert client.delete(f"/orders/{order['id']}", headers=jane).status_code == 403
    assert client.delete(f"/orders/{order['id']}", headers=admin).status_code == 200
    assert client.get(f"/orders/{order['id']}", headers=jane).status_code == 404
