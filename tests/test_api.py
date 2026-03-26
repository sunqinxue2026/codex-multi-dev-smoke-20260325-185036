from fastapi.testclient import TestClient

from snack_store.app import app

client = TestClient(app)


def test_healthcheck():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_get_snacks():
    response = client.get('/api/snacks')
    assert response.status_code == 200
    data = response.json()
    assert 'items' in data
    assert len(data['items']) >= 3
    # Verify featured field is present and boolean
    for item in data['items']:
        assert 'featured' in item
        assert isinstance(item['featured'], bool)


def test_create_order():
    response = client.post('/api/orders', json={'items': [{'id': 1, 'quantity': 2}]})
    assert response.status_code == 200
    assert response.json()['message'] == 'order_created'
