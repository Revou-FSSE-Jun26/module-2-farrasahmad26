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
