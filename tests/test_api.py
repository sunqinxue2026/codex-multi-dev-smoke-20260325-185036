from fastapi.testclient import TestClient

from snack_store.app import FREE_SHIPPING_THRESHOLD, app

client = TestClient(app)


def test_healthcheck():
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['version'] == '0.3.0'
    assert payload['service'] == 'snack-store'
    assert payload['catalog_size'] >= 8


def test_get_snacks_supports_filters():
    response = client.get('/api/snacks', params={'category': '烘焙甜点', 'sort': 'rating'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['total'] >= 2
    assert all(item['category'] == '烘焙甜点' for item in payload['items'])


def test_get_snack_meta():
    response = client.get('/api/snacks/meta')
    assert response.status_code == 200
    payload = response.json()
    assert any(item['name'] == '膨化精选' for item in payload['categories'])
    assert len(payload['spotlight']) == 3


def test_get_single_snack():
    response = client.get('/api/snacks/2')
    assert response.status_code == 200
    payload = response.json()
    assert payload['name'] == '抹茶夹心曲奇'
    assert payload['featured'] is True


def test_create_order_returns_summary():
    response = client.post(
        '/api/orders',
        json={'items': [{'id': 1, 'quantity': 2}, {'id': 5, 'quantity': 3}]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['message'] == 'order_created'
    assert payload['order_id'].startswith('SNK-')
    assert payload['total_items'] == 5
    assert payload['subtotal'] == (16 * 2) + (14 * 3)
    assert payload['shipping_fee'] == 0
    assert payload['subtotal'] >= FREE_SHIPPING_THRESHOLD
    assert payload['total_price'] == payload['subtotal'] - payload['discount']
    assert len(payload['items']) == 2
    assert len(payload['recommendations']) <= 2


def test_create_order_rejects_overstock():
    response = client.post('/api/orders', json={'items': [{'id': 7, 'quantity': 15}]})
    assert response.status_code == 400
    assert '库存不足' in response.json()['detail']


def test_root_without_frontend_build():
    response = client.get('/')
    assert response.status_code == 200
    content_type = response.headers.get('content-type', '')
    if 'application/json' in content_type:
        assert response.json()['message'] == 'Snack Store API'
    else:
        assert 'text/html' in content_type
        assert '<div id="root"></div>' in response.text
