def test_login_invalid_user(client):
    payload = {
        'username': 'test@gmail.com',
        'password': 'wrong'
    }
    response = client.post('/api/internal/auth/login',data=payload,  headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401

def test_me_endpoint_requires_auth(client):
    response = client.get('/api/internal/auth/me')
    assert response.status_code == 401

def test_me_endpoint_requires_success(auth_client):
    response = auth_client.get('/api/internal/auth/me')
    assert response.status_code == 200
