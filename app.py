#!/usr/bin/env python3
"""
Todo API - A simple Flask REST API for managing todos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import os

app = Flask(__name__)
CORS(app)

# In-memory storage for todos
todos = []

class Todo:
    """Todo model"""
    def __init__(self, title, description=""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = False
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
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
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if completed is not None:
            self.completed = completed
        self.updated_at = datetime.utcnow().isoformat()

def find_todo_by_id(todo_id):
    """Find todo by ID"""
    for todo in todos:
        if todo.id == todo_id:
            return todo
    return None

def validate_todo_data(data, required_fields=None):
    """Validate todo data"""
    if not data:
        return "Request body is required"
    
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                return f"Field '{field}' is required"
    
    if 'title' in data:
        if not isinstance(data['title'], str) or len(data['title'].strip()) == 0:
            return "Title must be a non-empty string"
        if len(data['title']) > 200:
            return "Title cannot exceed 200 characters"
    
    if 'description' in data:
        if not isinstance(data['description'], str):
            return "Description must be a string"
        if len(data['description']) > 1000:
            return "Description cannot exceed 1000 characters"
    
    if 'completed' in data:
        if not isinstance(data['completed'], bool):
            return "Completed must be a boolean"
    
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Todo API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/v1/todos', methods=['GET'])
def get_todos():
    """Get all todos with optional filtering"""
    try:
        filter_param = request.args.get('filter', 'all').lower()
        
        if filter_param == 'completed':
            filtered_todos = [todo for todo in todos if todo.completed]
        elif filter_param == 'pending':
            filtered_todos = [todo for todo in todos if not todo.completed]
        else:
            filtered_todos = todos
        
        return jsonify({
            'success': True,
            'data': [todo.to_dict() for todo in filtered_todos],
            'count': len(filtered_todos)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

@app.route('/api/v1/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        data = request.get_json()
        
        # Validate input
        error = validate_todo_data(data, required_fields=['title'])
        if error:
            return jsonify({
                'success': False,
                'error': {'message': error, 'status_code': 400}
            }), 400
        
        # Create todo
        todo = Todo(
            title=data['title'],
            description=data.get('description', '')
        )
        todos.append(todo)
        
        return jsonify({
            'success': True,
            'message': 'Todo created successfully',
            'data': todo.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

@app.route('/api/v1/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo by ID"""
    try:
        todo = find_todo_by_id(todo_id)
        
        if not todo:
            return jsonify({
                'success': False,
                'error': {'message': 'Todo not found', 'status_code': 404}
            }), 404
        
        return jsonify({
            'success': True,
            'data': todo.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

@app.route('/api/v1/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a specific todo"""
    try:
        data = request.get_json()
        
        # Validate input
        error = validate_todo_data(data)
        if error:
            return jsonify({
                'success': False,
                'error': {'message': error, 'status_code': 400}
            }), 400
        
        todo = find_todo_by_id(todo_id)
        if not todo:
            return jsonify({
                'success': False,
                'error': {'message': 'Todo not found', 'status_code': 404}
            }), 404
        
        # Update todo
        todo.update(
            title=data.get('title'),
            description=data.get('description'),
            completed=data.get('completed')
        )
        
        return jsonify({
            'success': True,
            'message': 'Todo updated successfully',
            'data': todo.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

@app.route('/api/v1/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a specific todo"""
    try:
        todo = find_todo_by_id(todo_id)
        
        if not todo:
            return jsonify({
                'success': False,
                'error': {'message': 'Todo not found', 'status_code': 404}
            }), 404
        
        todos.remove(todo)
        
        return jsonify({
            'success': True,
            'message': 'Todo deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

@app.route('/api/v1/todos/<todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    try:
        todo = find_todo_by_id(todo_id)
        
        if not todo:
            return jsonify({
                'success': False,
                'error': {'message': 'Todo not found', 'status_code': 404}
            }), 404
        
        # Toggle completion status
        todo.update(completed=not todo.completed)
        
        return jsonify({
            'success': True,
            'message': f'Todo marked as {"completed" if todo.completed else "pending"}',
            'data': todo.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

@app.route('/api/v1/todos/stats', methods=['GET'])
def get_todo_stats():
    """Get todo statistics"""
    try:
        total = len(todos)
        completed = len([todo for todo in todos if todo.completed])
        pending = total - completed
        completion_rate = round((completed / total) * 100, 2) if total > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'completed': completed,
                'pending': pending,
                'completion_rate': completion_rate
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'status_code': 500}
        }), 500

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