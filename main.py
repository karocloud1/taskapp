from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

if __name__ == '__main__':
    app.run(debug=True)

def create_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        due_date=data.get('due_date'),
        status=data.get('status', 'pending'),
        user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'})

@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.as_dict() for task in tasks])

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    data = request.get_json()
    task = Task.query.filter_by(id=task_id, user_id=get_jwt_identity()).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.due_date = data.get('due_date', task.due_date)
    task.status = data.get('status', task.status)
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=get_jwt_identity()).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({'username': user.username})

@app.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'], method='sha256')
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

# Add to the previous code

@app.route('/tasks/<int:task_id>/assign', methods=['PUT'])
@jwt_required()
def assign_task(task_id):
    data = request.get_json()
    task = Task.query.filter_by(id=task_id, user_id=get_jwt_identity()).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    task.user_id = data['user_id']
    db.session.commit()
    return jsonify({'message': 'Task assigned successfully'})

@app.route('/users/<int:user_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks_by_user(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.as_dict() for task in tasks])

# Add to the previous code

@app.route('/tasks/search', methods=['GET'])
@jwt_required()
def search_tasks():
    query = request.args.get('q')
    user_id = get_jwt_identity()
    tasks = Task.query.filter(Task.user_id == user_id, Task.title.contains(query) | Task.description.contains(query)).all()
    return jsonify([task.as_dict() for task in tasks])

@app.route('/tasks/filter', methods=['GET'])
@jwt_required()
def filter_tasks():
    user_id = get_jwt_identity()
    status = request.args.get('status')
    due_date = request.args.get('due_date')
    tasks_query = Task.query.filter_by(user_id=user_id)
    if status:
        tasks_query = tasks_query.filter_by(status=status)
    if due_date:
        tasks_query = tasks_query.filter_by(due_date=due_date)
    tasks = tasks_query.all()
    return jsonify([task.as_dict() for task in tasks])



@app.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'message': 'Unauthorized'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Task Management API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)