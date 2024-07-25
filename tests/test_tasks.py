import pytest
from main import app, db, User, Task
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/taskmngmt'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables for each test
            # Optionally, create any necessary test data here
            yield client
            db.session.remove()
            db.drop_all()  # Drop tables after tests

def auth_header(client, username='testuser5'):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}
    

def test_create_task(client):
    headers = auth_header(client)
    response = client.post('/tasks', json={'title': 'Test Task', 'description': 'Test Description'}, headers=headers)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Task created successfully'

def test_get_tasks(client):
    headers = auth_header(client)
    client.post('/tasks', json={'title': 'Test Task', 'description': 'Test Description'}, headers=headers)
    response = client.get('/tasks', headers=headers)
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test Task'

def test_update_task(client):
    headers = auth_header(client)
    client.post('/tasks', json={'title': 'Test Task', 'description': 'Test Description'}, headers=headers)
    response = client.put('/tasks/1', json={'title': 'Updated Task'}, headers=headers)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Task updated successfully'

def test_delete_task(client):
    headers = auth_header(client)
    client.post('/tasks', json={'title': 'Test Task', 'description': 'Test Description'}, headers=headers)
    response = client.delete('/tasks/1', headers=headers)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Task deleted successfully'
