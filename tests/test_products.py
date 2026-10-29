import pytest


@pytest.fixture(scope='module')
def client(app, admin_headers):
    # Product write endpoints are admin-only, so this module's client sends an admin
    # token by default. Auth rules themselves are tested below with explicit clients.
    c = app.test_client()
    c.environ_base['HTTP_AUTHORIZATION'] = admin_headers['Authorization']
    return c

def test_get_all_products(client):
    response = client.get('/products')

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert 'id' in data[0]
    assert 'name' in data[0]
    assert 'price' in data[0]
    assert 'stock_quantity' in data[0]
    assert 'created_at' in data[0]


def test_create_product_returns_201(client):
    payload = {
        'name': 'Mouse',
        'price': 49.99,
        'stock_quantity': 1,
        'category_id': 1,
    }
    response = client.post('/products', json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['name'] == 'Mouse'
    assert float(data['price']) == 49.99
    assert data['stock_quantity'] == 1
    assert data['category_id'] == 1
    assert 'created_at' in data


def test_create_product_missing_name_returns_400(client):
    payload = {
        'price': 49.99,
        'stock_quantity': 1,
        'category_id': 1,
    }
    response = client.post('/products', json=payload)

    assert response.status_code == 400


def test_create_product_negative_price_returns_422(client):
    payload = {
        'name': 'Mouse',
        'price': -49.99,
        'stock_quantity': 1,
        'category_id': 1,
    }
    response = client.post('/products', json=payload)

    assert response.status_code == 422


def test_get_product_by_id_returns_200(client):
    response = client.get('/products/1')

    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Laptop Gaming'


def test_get_product_nonexistent_returns_404(client):
    response = client.get('/products/999')

    assert response.status_code == 404


def test_update_product_returns_200(client):
    update = {'price': 2499.99}
    response = client.put('/products/1', json=update)

    assert response.status_code == 200
    data = response.get_json()
    assert float(data['price']) == 2499.99


def test_update_nonexistent_product_returns_404(client):
    update = {'price': 1499.99}
    response = client.put('/products/999', json=update)

    assert response.status_code == 404


def test_delete_product_returns_200(client):
    create_response = client.post('/products', json={
        'name': 'Test item',
        'price': 59.99,
        'stock_quantity': 1,
        'category_id': 1,
    })
    new_id = create_response.get_json()['id']

    delete_response = client.delete(f'/products/{new_id}')
    assert delete_response.status_code == 200


def test_get_product_by_slug_returns_200(client):
    response = client.get('/products/laptop-gaming')

    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Laptop Gaming'
    assert data['slug'] == 'laptop-gaming'


def test_get_product_by_nonexistent_slug_returns_404(client):
    response = client.get('/products/does-not-exist')

    assert response.status_code == 404


def test_create_product_generates_slug_from_name(client):
    response = client.post('/products', json={
        'name': '  Mechanical Keyboard RGB!  ',
        'price': 89.99,
        'stock_quantity': 3,
        'category_id': 1,
    })

    assert response.status_code == 201
    assert response.get_json()['slug'] == 'mechanical-keyboard-rgb'


def test_create_product_duplicate_name_gets_unique_slug(client):
    payload = {'name': 'USB Hub', 'price': 19.99, 'stock_quantity': 5, 'category_id': 1}
    first = client.post('/products', json=payload)
    second = client.post('/products', json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json()['slug'] == 'usb-hub'
    assert second.get_json()['slug'] == 'usb-hub-2'


def test_create_product_uses_custom_slug(client):
    response = client.post('/products', json={
        'name': 'Desk Lamp',
        'slug': 'Lampu Meja',
        'price': 29.99,
        'stock_quantity': 2,
        'category_id': 1,
    })

    assert response.status_code == 201
    assert response.get_json()['slug'] == 'lampu-meja'


def test_numeric_name_slug_does_not_clash_with_id_route(client):
    create_response = client.post('/products', json={
        'name': '2026',
        'price': 9.99,
        'stock_quantity': 1,
        'category_id': 1,
    })
    slug = create_response.get_json()['slug']
    assert slug == 'product-2026'

    response = client.get(f'/products/{slug}')
    assert response.status_code == 200
    assert response.get_json()['name'] == '2026'


def test_get_deleted_product_by_slug_returns_404(client):
    create_response = client.post('/products', json={
        'name': 'Temporary Item',
        'price': 5.0,
        'stock_quantity': 1,
        'category_id': 1,
    })
    data = create_response.get_json()
    client.delete(f"/products/{data['id']}")

    response = client.get(f"/products/{data['slug']}")
    assert response.status_code == 404


# ---- Admin-only writes & inactive products ----

PAYLOAD = {'name': 'Auth Test Item', 'price': 9.99, 'stock_quantity': 1, 'category_id': 1}


@pytest.mark.parametrize('method,path', [
    ('post', '/products'),
    ('put', '/products/1'),
    ('delete', '/products/1'),
    ('put', '/products/restore/1'),
])
def test_product_writes_require_login(app, method, path):
    anon = app.test_client()
    response = getattr(anon, method)(path, json=PAYLOAD)
    assert response.status_code == 401


@pytest.mark.parametrize('method,path', [
    ('post', '/products'),
    ('put', '/products/1'),
    ('delete', '/products/1'),
    ('put', '/products/restore/1'),
])
def test_product_writes_forbidden_for_customers(app, user_headers, method, path):
    response = getattr(app.test_client(), method)(path, json=PAYLOAD, headers=user_headers)
    assert response.status_code == 403


def test_include_inactive_requires_admin(app, user_headers):
    anon = app.test_client()
    assert anon.get('/products?include_inactive=true').status_code == 401
    assert anon.get('/products?include_inactive=true', headers=user_headers).status_code == 403


def test_deactivate_and_restore_product(client, app):
    new_id = client.post('/products', json={**PAYLOAD, 'name': 'Seasonal Blend'}).get_json()['id']

    assert client.delete(f'/products/{new_id}').status_code == 200

    # Hidden from the public list and detail...
    public = app.test_client()
    assert new_id not in [p['id'] for p in public.get('/products').get_json()]
    assert public.get(f'/products/{new_id}').status_code == 404

    # ...but visible (and marked inactive) for the admin dashboard.
    admin_list = client.get('/products?include_inactive=true').get_json()
    item = next(p for p in admin_list if p['id'] == new_id)
    assert item['is_active'] is False

    restored = client.put(f'/products/restore/{new_id}')
    assert restored.status_code == 200
    assert restored.get_json()['product']['is_active'] is True
    assert public.get(f'/products/{new_id}').status_code == 200


# ---- Edit page support ----

def test_admin_can_load_inactive_product_by_id(client, app, user_headers):
    new_id = client.post('/products', json={**PAYLOAD, 'name': 'Hidden Kettle'}).get_json()['id']
    client.delete(f'/products/{new_id}')

    public = app.test_client()
    assert public.get(f'/products/{new_id}').status_code == 404
    assert public.get(f'/products/{new_id}?include_inactive=true').status_code == 401
    assert public.get(f'/products/{new_id}?include_inactive=true', headers=user_headers).status_code == 403

    response = client.get(f'/products/{new_id}?include_inactive=true')
    assert response.status_code == 200
    assert response.get_json()['is_active'] is False
    assert client.get('/products/99999?include_inactive=true').status_code == 404


def test_update_description_and_image(client):
    new_id = client.post('/products', json={**PAYLOAD, 'name': 'Editable Scale'}).get_json()['id']

    data = client.put(f'/products/{new_id}', json={
        'description': '  Accurate to 0.1g  ',
        'image': 'https://example.com/scale.jpg',
    }).get_json()
    assert data['description'] == 'Accurate to 0.1g'
    assert data['image'] == 'https://example.com/scale.jpg'

    # Empty strings clear both fields.
    data = client.put(f'/products/{new_id}', json={'description': '', 'image': ''}).get_json()
    assert data['description'] is None
    assert data['image'] is None


@pytest.mark.parametrize('payload,code', [
    ({'image': 'not-a-url'}, 422),
    ({'image': 123}, 400),
    ({'description': 'x' * 501}, 422),
    ({'description': 5}, 400),
])
def test_update_product_invalid_description_or_image(client, payload, code):
    assert client.put('/products/1', json=payload).status_code == code
