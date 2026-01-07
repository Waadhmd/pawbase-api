def test_create_user(client):
    '''
    What this test proves: FastAPI routing works,
    Dependency override works, Database works,
   SQLModel works, Response schema works
    '''
    #print([route.path for route in client.app.routes])

    payload = {
        'email': 'test_user@gamil.com',
        'password': 'testshelter123',
        'role': 'org_admin'
    }
    response = client.post('/api/internal/users/signup', json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['email'] == payload['email']
    assert 'id' in data