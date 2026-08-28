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