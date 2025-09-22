#!/usr/bin/env python3
"""
Todo API - A robust Flask REST API for managing todos with comprehensive validation and logging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import os
import logging
import re
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('todo_api.log') if os.environ.get('FLASK_ENV') != 'production' else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Enhanced configuration
app.config.update(
    JSON_SORT_KEYS=False,
    JSONIFY_PRETTYPRINT_REGULAR=True,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max request size
)

# In-memory storage for todos
todos = []

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class Todo:
    """Enhanced Todo model with validation"""
    def __init__(self, title, description=""):
        # Validate inputs during creation
        self._validate_title(title)
        self._validate_description(description)
        
        self.id = str(uuid.uuid4())
        self.title = title.strip()
        self.description = description.strip()
        self.completed = False
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        
        logger.info(f"Created new todo: {self.id}")
    
    @staticmethod
    def _validate_title(title):
        """Validate todo title"""
        if not title or not isinstance(title, str):
            raise ValidationError("Title is required and must be a string")
        
        title = title.strip()
        if not title:
            raise ValidationError("Title cannot be empty or whitespace only")
        
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")
        
        # Check for potentially malicious content
        if re.search(r'[<>"\'&]', title):
            raise ValidationError("Title contains invalid characters")
    
    @staticmethod
    def _validate_description(description):
        """Validate todo description"""
        if description is not None:
            if not isinstance(description, str):
                raise ValidationError("Description must be a string")
            
            if len(description) > 1000:
                raise ValidationError("Description cannot exceed 1000 characters")
    
    @staticmethod
    def _validate_completed(completed):
        """Validate completed status"""
        if completed is not None and not isinstance(completed, bool):
            raise ValidationError("Completed must be a boolean value")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def update(self, title=None, description=None, completed=None):
        """Update todo with validation"""
        if title is not None:
            self._validate_title(title)
            self.title = title.strip()
        
        if description is not None:
            self._validate_description(description)
            self.description = description.strip()
        
        if completed is not None:
            self._validate_completed(completed)
            self.completed = completed
        
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Updated todo: {self.id}")

def error_handler(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e.message}")
            return jsonify({
                'success': False,
                'error': {
                    'message': e.message,
                    'status_code': e.status_code,
                    'type': 'validation_error'
                }
            }), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'message': 'An internal server error occurred',
                    'status_code': 500,
                    'type': 'server_error'
                }
            }), 500
    return decorated_function

def validate_json_content_type():
    """Validate JSON content type for POST/PUT requests"""
    if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type != 'application/json':
        raise ValidationError("Content-Type must be application/json", 415)

def validate_todo_id(todo_id):
    """Validate todo ID format"""
    try:
        uuid.UUID(todo_id)
    except ValueError:
        raise ValidationError("Invalid todo ID format", 400)

def find_todo_by_id(todo_id):
    """Find todo by ID with validation"""
    validate_todo_id(todo_id)
    for todo in todos:
        if todo.id == todo_id:
            return todo
    return None

def validate_request_data(data, required_fields=None):
    """Enhanced validation for request data"""
    if not data:
        raise ValidationError("Request body is required")
    
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")
    
    # Check for required fields
    if required_fields:
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Required field '{field}' is missing")
    
    # Validate individual fields if present
    if 'title' in data:
        Todo._validate_title(data['title'])
    
    if 'description' in data:
        Todo._validate_description(data['description'])
    
    if 'completed' in data:
        Todo._validate_completed(data['completed'])

def validate_filter_param(filter_param):
    """Validate filter parameter"""
    valid_filters = ['all', 'completed', 'pending']
    if filter_param and filter_param.lower() not in valid_filters:
        raise ValidationError(f"Invalid filter parameter. Must be one of: {', '.join(valid_filters)}")
    return filter_param.lower() if filter_param else 'all'

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    logger.warning("Request entity too large")
    return jsonify({
        'success': False,
        'error': {
            'message': 'Request entity too large. Maximum size is 16MB.',
            'status_code': 413,
            'type': 'request_too_large'
        }
    }), 413

@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {error}")
    return jsonify({
        'success': False,
        'error': {
            'message': 'Bad request. Please check your request format.',
            'status_code': 400,
            'type': 'bad_request'
        }
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'message': 'The requested resource was not found.',
            'status_code': 404,
            'type': 'not_found'
        }
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': {
            'message': 'Method not allowed for this endpoint.',
            'status_code': 405,
            'type': 'method_not_allowed'
        }
    }), 405

@app.route('/health', methods=['GET'])
@error_handler
def health_check():
    """Health check endpoint with enhanced logging"""
    logger.info("Health check requested")
    return jsonify({
        'status': 'healthy',
        'message': 'Todo API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'total_todos': len(todos)
    }), 200

@app.route('/api/v1/todos', methods=['GET'])
@error_handler
def get_todos():
    """Get all todos with enhanced filtering and validation"""
    logger.info("Get todos requested")
    
    filter_param = validate_filter_param(request.args.get('filter', 'all'))
    
    if filter_param == 'completed':
        filtered_todos = [todo for todo in todos if todo.completed]
    elif filter_param == 'pending':
        filtered_todos = [todo for todo in todos if not todo.completed]
    else:
        filtered_todos = todos
    
    logger.info(f"Returning {len(filtered_todos)} todos with filter: {filter_param}")
    
    return jsonify({
        'success': True,
        'data': [todo.to_dict() for todo in filtered_todos],
        'count': len(filtered_todos),
        'filter': filter_param,
        'total_todos': len(todos)
    }), 200

@app.route('/api/v1/todos', methods=['POST'])
@error_handler
def create_todo():
    """Create a new todo with enhanced validation"""
    logger.info("Create todo requested")
    
    validate_json_content_type()
    data = request.get_json()
    validate_request_data(data, required_fields=['title'])
    
    # Create todo (validation happens in constructor)
    todo = Todo(
        title=data['title'],
        description=data.get('description', '')
    )
    todos.append(todo)
    
    logger.info(f"Successfully created todo: {todo.id}")
    
    return jsonify({
        'success': True,
        'message': 'Todo created successfully',
        'data': todo.to_dict()
    }), 201

@app.route('/api/v1/todos/<todo_id>', methods=['GET'])
@error_handler
def get_todo(todo_id):
    """Get a specific todo by ID with validation"""
    logger.info(f"Get todo requested: {todo_id}")
    
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        logger.warning(f"Todo not found: {todo_id}")
        raise ValidationError('Todo not found', 404)
    
    logger.info(f"Successfully retrieved todo: {todo_id}")
    
    return jsonify({
        'success': True,
        'data': todo.to_dict()
    }), 200

@app.route('/api/v1/todos/<todo_id>', methods=['PUT'])
@error_handler
def update_todo(todo_id):
    """Update a specific todo with enhanced validation"""
    logger.info(f"Update todo requested: {todo_id}")
    
    validate_json_content_type()
    data = request.get_json()
    validate_request_data(data)
    
    todo = find_todo_by_id(todo_id)
    if not todo:
        logger.warning(f"Todo not found for update: {todo_id}")
        raise ValidationError('Todo not found', 404)
    
    # Update todo (validation happens in update method)
    todo.update(
        title=data.get('title'),
        description=data.get('description'),
        completed=data.get('completed')
    )
    
    logger.info(f"Successfully updated todo: {todo_id}")
    
    return jsonify({
        'success': True,
        'message': 'Todo updated successfully',
        'data': todo.to_dict()
    }), 200

@app.route('/api/v1/todos/<todo_id>', methods=['DELETE'])
@error_handler
def delete_todo(todo_id):
    """Delete a specific todo with validation"""
    logger.info(f"Delete todo requested: {todo_id}")
    
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        logger.warning(f"Todo not found for deletion: {todo_id}")
        raise ValidationError('Todo not found', 404)
    
    todos.remove(todo)
    logger.info(f"Successfully deleted todo: {todo_id}")
    
    return jsonify({
        'success': True,
        'message': 'Todo deleted successfully'
    }), 200

@app.route('/api/v1/todos/<todo_id>/toggle', methods=['PATCH'])
@error_handler
def toggle_todo(todo_id):
    """Toggle todo completion status with validation"""
    logger.info(f"Toggle todo requested: {todo_id}")
    
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        logger.warning(f"Todo not found for toggle: {todo_id}")
        raise ValidationError('Todo not found', 404)
    
    # Toggle completion status
    todo.update(completed=not todo.completed)
    
    status = "completed" if todo.completed else "pending"
    logger.info(f"Successfully toggled todo {todo_id} to {status}")
    
    return jsonify({
        'success': True,
        'message': f'Todo marked as {status}',
        'data': todo.to_dict()
    }), 200

@app.route('/api/v1/todos/stats', methods=['GET'])
@error_handler
def get_todo_stats():
    """Get comprehensive todo statistics"""
    logger.info("Todo stats requested")
    
    total = len(todos)
    completed = len([todo for todo in todos if todo.completed])
    pending = total - completed
    completion_rate = round((completed / total) * 100, 2) if total > 0 else 0
    
    # Additional stats
    recent_todos = len([
        todo for todo in todos 
        if datetime.fromisoformat(todo.created_at.replace('Z', '+00:00')).date() == datetime.utcnow().date()
    ])
    
    stats = {
        'total': total,
        'completed': completed,
        'pending': pending,
        'completion_rate': completion_rate,
        'created_today': recent_todos
    }
    
    logger.info(f"Stats generated: {stats}")
    
    return jsonify({
        'success': True,
        'data': stats
    }), 200

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    print(f"Starting Todo API server...")
    print(f"Server: http://{host}:{port}")
    print(f"Health check: http://{host}:{port}/health")
    print(f"API Base URL: http://{host}:{port}/api/v1")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)