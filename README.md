# Todo API

A simple, yet powerful REST API for managing todos built with Flask. This API provides full CRUD operations, filtering capabilities, and comprehensive statistics for todo management.

## Features

- ✅ **Full CRUD Operations**: Create, Read, Update, Delete todos
- 🔍 **Filtering**: Filter todos by completion status
- 📊 **Statistics**: Get comprehensive stats about your todos
- 🚀 **Production Ready**: Docker support with multi-stage builds
- 🔒 **Secure**: Non-root container user and input validation
- 🎯 **RESTful Design**: Clean, consistent API endpoints
- 📝 **Comprehensive Documentation**: Full API reference with examples

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jogi1549/agentic-workflow-demo.git
   cd agentic-workflow-demo
   ```

2. **Build and run with Docker**:
   ```bash
   docker build -t todo-api .
   docker run -p 5001:5001 todo-api
   ```

3. **Access the API**:
   - API Base URL: `http://localhost:5001/api/v1`
   - Health Check: `http://localhost:5001/health`

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Configure environment (optional)**:
   ```bash
   export FLASK_HOST=0.0.0.0
   export FLASK_PORT=5000
   export FLASK_DEBUG=True
   ```

## API Reference

### Base URL
```
http://localhost:5001/api/v1
```

### Authentication
No authentication required for this demo API.

### Endpoints

#### Health Check
```http
GET /health
```
Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Todo API is running",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Get All Todos
```http
GET /api/v1/todos?filter={all|completed|pending}
```

**Query Parameters:**
- `filter` (optional): Filter todos by status
  - `all` (default): Return all todos
  - `completed`: Return only completed todos
  - `pending`: Return only pending todos

**Example Request:**
```bash
curl -X GET "http://localhost:5001/api/v1/todos?filter=pending"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Learn Docker",
      "description": "Complete Docker tutorial and build first container",
      "completed": false,
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "count": 1
}
```

#### Create Todo
```http
POST /api/v1/todos
```

**Request Body:**
```json
{
  "title": "Learn Flask",
  "description": "Build a REST API with Flask framework"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5001/api/v1/todos" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Flask", "description": "Build a REST API"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Todo created successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Learn Flask",
    "description": "Build a REST API with Flask framework",
    "completed": false,
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
}
```

#### Get Single Todo
```http
GET /api/v1/todos/{id}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5001/api/v1/todos/123e4567-e89b-12d3-a456-426614174000"
```

#### Update Todo
```http
PUT /api/v1/todos/{id}
```

**Request Body:**
```json
{
  "title": "Learn Advanced Flask",
  "description": "Master Flask with authentication and testing",
  "completed": true
}
```

**Example Request:**
```bash
curl -X PUT "http://localhost:5001/api/v1/todos/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Advanced Flask", "completed": true}'
```

#### Delete Todo
```http
DELETE /api/v1/todos/{id}
```

**Example Request:**
```bash
curl -X DELETE "http://localhost:5001/api/v1/todos/123e4567-e89b-12d3-a456-426614174000"
```

#### Toggle Todo Status
```http
PATCH /api/v1/todos/{id}/toggle
```

**Example Request:**
```bash
curl -X PATCH "http://localhost:5001/api/v1/todos/123e4567-e89b-12d3-a456-426614174000/toggle"
```

#### Get Todo Statistics
```http
GET /api/v1/todos/stats
```

**Example Request:**
```bash
curl -X GET "http://localhost:5001/api/v1/todos/stats"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 10,
    "completed": 7,
    "pending": 3,
    "completion_rate": 70.0
  }
}
```

## Data Models

### Todo Object
```json
{
  "id": "string (UUID)",
  "title": "string (required, max 200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "status_code": 400
  }
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

## Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:5001/api/v1"

# Create a new todo
def create_todo(title, description=""):
    response = requests.post(
        f"{BASE_URL}/todos",
        json={"title": title, "description": description}
    )
    return response.json()

# Get all todos
def get_todos(filter_status="all"):
    response = requests.get(f"{BASE_URL}/todos", params={"filter": filter_status})
    return response.json()

# Update todo
def update_todo(todo_id, **kwargs):
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=kwargs)
    return response.json()

# Delete todo
def delete_todo(todo_id):
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    return response.json()

# Example usage
if __name__ == "__main__":
    # Create todo
    result = create_todo("Learn Python", "Complete Python tutorial")
    todo_id = result["data"]["id"]
    
    # Get all todos
    todos = get_todos()
    print(f"Total todos: {todos['count']}")
    
    # Update todo
    update_todo(todo_id, completed=True)
    
    # Get statistics
    stats = requests.get(f"{BASE_URL}/todos/stats").json()
    print(f"Completion rate: {stats['data']['completion_rate']}%")
```

## Docker Commands

### Build Image
```bash
docker build -t todo-api .
```

### Run Container
```bash
# Run on default port 5001
docker run -p 5001:5001 todo-api

# Run with custom port
docker run -p 8080:5001 todo-api

# Run with environment variables
docker run -p 5001:5001 -e FLASK_DEBUG=False todo-api

# Run in background
docker run -d -p 5001:5001 --name todo-api-container todo-api
```

### Container Management
```bash
# View logs
docker logs todo-api-container

# Stop container
docker stop todo-api-container

# Remove container
docker rm todo-api-container

# Health check
docker exec todo-api-container python -c "import requests; print(requests.get('http://localhost:5001/health').json())"
```

## Environment Variables

Configure the application using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_HOST` | `0.0.0.0` | Host to bind the server |
| `FLASK_PORT` | `5000` | Port to run the server |
| `FLASK_DEBUG` | `False` | Enable debug mode |

## Production Deployment

### Using Docker Compose
Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  todo-api:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_DEBUG=False
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5001/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

### Using Kubernetes
Example deployment configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
    spec:
      containers:
      - name: todo-api
        image: todo-api:latest
        ports:
        - containerPort: 5001
        env:
        - name: FLASK_DEBUG
          value: "False"
        livenessProbe:
          httpGet:
            path: /health
            port: 5001
          initialDelaySeconds: 30
          periodSeconds: 30
```

## Development

### Project Structure
```
agentic-workflow-demo/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── README.md          # This file
└── .gitignore        # Git ignore rules
```

### Adding Features

To extend the API:

1. **Add new endpoints** in `app.py`
2. **Update the Todo model** if needed
3. **Add validation** for new fields
4. **Update this README** with new endpoints

### Testing

Test the API manually using curl or tools like Postman:

```bash
# Test health endpoint
curl http://localhost:5001/health

# Test creating a todo
curl -X POST "http://localhost:5001/api/v1/todos" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Todo", "description": "Testing the API"}'

# Test getting todos
curl http://localhost:5001/api/v1/todos

# Test statistics
curl http://localhost:5001/api/v1/todos/stats
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change port in environment variable
   export FLASK_PORT=5002
   python app.py
   ```

2. **Docker build fails**:
   ```bash
   # Clear Docker cache
   docker builder prune
   docker build --no-cache -t todo-api .
   ```

3. **Health check fails**:
   ```bash
   # Check if service is running
   curl http://localhost:5001/health
   
   # Check Docker logs
   docker logs todo-api-container
   ```

### Debug Mode

Enable debug mode for development:
```bash
export FLASK_DEBUG=True
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please open an issue in the GitHub repository.