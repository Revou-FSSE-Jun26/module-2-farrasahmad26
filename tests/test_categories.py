import pytest


@pytest.fixture(scope='module')
def client(app, admin_headers):
    # Category write endpoints are admin-only; this module's client sends an admin token.
    c = app.test_client()
    c.environ_base['HTTP_AUTHORIZATION'] = admin_headers['Authorization']
    return c


def test_get_all_categories(client):
    response = client.get('/categories')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert 'id' in data[0]
    assert 'name' in data[0]
    assert 'is_active' in data[0]
    assert 'created_at' in data[0]

def test_create_category_returns_201(client):
    payload = {
        'name': 'Coffee'
    }
    response = client.post('/categories', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['name'] == 'Coffee'
    assert 'created_at' in data

def test_create_category_missing_name_returns_400(client):
    payload = {
        'description': 'A variety of coffee type'
    }
    response = client.post('/categories', json=payload)
    assert response.status_code == 400

def test_get_category_by_id_returns_200(client):
    response = client.get('/categories/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Electronics'

def test_get_category_nonexistent_returns_404(client):
    response = client.get('/categories/999')
    assert response.status_code == 404

def test_update_category_returns_200(client):
    update = {'description': 'A list variety of electronic'}
    response = client.put('/categories/1', json=update)
    assert response.status_code == 200
    data = response.get_json()
    assert data['description'] == 'A list variety of electronic'

def test_update_nonexistent_category_returns_404(client):
    update = {'description': 'A list of many electronic devices'}
    response = client.put('/categories/999', json=update)
    assert response.status_code == 404

def test_delete_category_returns_200(client):
    create_response = client.post('/categories', json={
        'name': 'Test category'
    })
    new_id = create_response.get_json()['id']
    delete_response = client.delete(f'/categories/{new_id}')
    assert delete_response.status_code == 200

def test_delete_nonexistent_category_returns_404(client):
    response = client.delete('/categories/999')
    assert response.status_code == 404


IMAGE_URL = 'https://example.com/images/grinder.jpg'


def test_get_all_categories_includes_image_field(client):
    response = client.get('/categories')
    assert response.status_code == 200
    assert 'image' in response.get_json()[0]


def test_create_category_with_image_returns_201(client):
    response = client.post('/categories', json={'name': 'Coffee Grinder', 'image': IMAGE_URL})
    assert response.status_code == 201
    assert response.get_json()['image'] == IMAGE_URL


def test_create_category_without_image_is_null(client):
    response = client.post('/categories', json={'name': 'Coffee Scale'})
    assert response.status_code == 201
    assert response.get_json()['image'] is None


def test_update_category_image_does_not_touch_description(client):
    client.put('/categories/1', json={'description': 'Original description'})

    response = client.put('/categories/1', json={'image': IMAGE_URL})
    assert response.status_code == 200
    data = response.get_json()
    assert data['image'] == IMAGE_URL
    assert data['description'] == 'Original description'

    # The change is persisted, not just echoed back.
    assert client.get('/categories/1').get_json()['image'] == IMAGE_URL


def test_update_category_empty_image_clears_it(client):
    client.put('/categories/1', json={'image': IMAGE_URL})

    response = client.put('/categories/1', json={'image': ''})
    assert response.status_code == 200
    assert response.get_json()['image'] is None


def test_create_category_image_not_string_returns_400(client):
    response = client.post('/categories', json={'name': 'Kettle', 'image': 123})
    assert response.status_code == 400


def test_create_category_image_invalid_url_returns_422(client):
    response = client.post('/categories', json={'name': 'Kettle', 'image': 'not-a-url'})
    assert response.status_code == 422


def test_update_category_image_invalid_url_returns_422(client):
    response = client.put('/categories/1', json={'image': 'ftp://example.com/a.jpg'})
    assert response.status_code == 422


# ---- Admin dashboard support ----

@pytest.mark.parametrize('method,path', [
    ('post', '/categories'),
    ('put', '/categories/1'),
    ('delete', '/categories/1'),
    ('put', '/categories/restore/1'),
])
def test_category_writes_require_admin(app, user_headers, method, path):
    anon = app.test_client()
    assert getattr(anon, method)(path, json={'name': 'X'}).status_code == 401
    assert getattr(anon, method)(path, json={'name': 'X'}, headers=user_headers).status_code == 403


def test_include_inactive_categories_requires_admin(app, user_headers):
    anon = app.test_client()
    assert anon.get('/categories?include_inactive=true').status_code == 401
    assert anon.get('/categories?include_inactive=true', headers=user_headers).status_code == 403


def test_product_count_counts_only_active_products(client):
    electronics = client.get('/categories/1').get_json()
    active = len(electronics['products'])
    assert electronics['product_count'] == active

    new_id = client.post('/products', json={'name': 'Counted Item', 'price': 5, 'stock_quantity': 1, 'category_id': 1}).get_json()['id']
    assert client.get('/categories/1').get_json()['product_count'] == active + 1

    client.delete(f'/products/{new_id}')
    assert client.get('/categories/1').get_json()['product_count'] == active


def test_cannot_deactivate_category_with_active_products(client):
    response = client.delete('/categories/1')
    assert response.status_code == 409
    assert 'active product' in response.get_json()['error']
    assert client.get('/categories/1').status_code == 200


def test_deactivate_and_restore_empty_category(client, app):
    new_id = client.post('/categories', json={'name': 'Seasonal'}).get_json()['id']
    assert client.delete(f'/categories/{new_id}').status_code == 200

    public = app.test_client()
    assert new_id not in [c['id'] for c in public.get('/categories').get_json()]
    assert public.get(f'/categories/{new_id}').status_code == 404

    listed = client.get('/categories?include_inactive=true').get_json()
    assert next(c for c in listed if c['id'] == new_id)['is_active'] is False
    assert client.get(f'/categories/{new_id}?include_inactive=true').status_code == 200

    restored = client.put(f'/categories/restore/{new_id}')
    assert restored.status_code == 200
    assert restored.get_json()['category']['is_active'] is True


def test_update_category_description_trim_and_clear(client):
    new_id = client.post('/categories', json={'name': 'Filters'}).get_json()['id']
    assert client.put(f'/categories/{new_id}', json={'description': '  Paper filters  '}).get_json()['description'] == 'Paper filters'
    assert client.put(f'/categories/{new_id}', json={'description': ''}).get_json()['description'] is None
    assert client.put(f'/categories/{new_id}', json={'description': 'x' * 501}).status_code == 422
    assert client.put(f'/categories/{new_id}', json={'description': 5}).status_code == 400
