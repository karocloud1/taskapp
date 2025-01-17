import pytest
from main import app, db, User
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/taskmngmt'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables for each test
            # Create a test user here to be used in authentication
            test_user = User(username='testuser5', password_hash='testpass5')
            db.session.add(test_user)
            db.session.commit()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Drop tables after tests

def auth_header(client, username='testuser5'):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            pytest.fail(f"User with username '{username}' not found.")
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}
    
def test_register(client):
    response = client.post('/register', json={'username': 'testuser5', 'password': 'testpass5'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User registered successfully'

def test_login(client):
    # Ensure test user is registered
    response = client.post('/register', json={'username': 'testuser5', 'password': 'testpass5'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User registered successfully'
    
    # Attempt login
    response = client.post('/login', json={'username': 'testuser5', 'password': 'testpass5'})
    assert response.status_code == 200
    assert 'access_token' in response.get_json()
