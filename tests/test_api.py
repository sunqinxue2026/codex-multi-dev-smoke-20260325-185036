from fastapi.testclient import TestClient

from snack_store.app import app

client = TestClient(app)


def test_healthcheck():
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['version'] == '0.2.0'
    assert payload['service'] == 'snack-store'


def test_get_snacks():
    response = client.get('/api/snacks')
    assert response.status_code == 200
    assert len(response.json()['items']) >= 3


def test_create_order():
    response = client.post('/api/orders', json={'items': [{'id': 1, 'quantity': 2}]})
    assert response.status_code == 200
    assert response.json()['message'] == 'order_created'


def test_root_without_frontend_build():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['message'] == 'Snack Store API'
