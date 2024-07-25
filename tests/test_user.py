import pytest
from main import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/taskmngmt'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def auth_header(client, username='testuser5'):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise Exception(f"User with username '{username}' not found.")
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}
    
def test_register(client):
    # Check if the user already exists and delete if necessary
    existing_user = User.query.filter_by(username='testuser5').first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()

    response = client.post('/register', json={'username': 'testuser5', 'password': 'testpass5'})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User registered successfully'

def test_login(client):
    # Ensure user registration before login
    client.post('/register', json={'username': 'testuser5', 'password': 'testpass5'})
    response = client.post('/login', json={'username': 'testuser5', 'password': 'testpass5'})
    assert response.status_code == 200
    assert 'access_token' in response.get_json()
