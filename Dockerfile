# Multi-stage build for Todo API
FROM python:3.11-slim as builder

# Set build arguments
ARG PYTHON_VERSION=3.11

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5001 \
    FLASK_DEBUG=False

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY app.py .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health')" || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "30", "--log-level", "info", "app:app"]