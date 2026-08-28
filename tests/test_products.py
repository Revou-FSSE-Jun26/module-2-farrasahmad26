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

