import pytest
from main import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register(client):
    response = client.post('/register', json={'username': 'test', 'password': 'test'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User registered successfully'
