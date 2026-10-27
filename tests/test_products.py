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
