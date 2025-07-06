# Use the latest Python slim image for security patches
FROM python:3.10-slim-bookworm

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Update system packages and install security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        sqlite3 \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory with proper permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_PATH=/app/data/northwind.db
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]