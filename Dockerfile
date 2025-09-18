# Rick AI Expert with RAG - Production Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Copy the precious Anterix knowledge database (our "memories")
COPY data/anterix_full_site.db /app/data/anterix_full_site.db

# Verify database was copied successfully
RUN ls -la /app/data/ && echo "✅ Anterix knowledge database included in deployment"

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port for Rick with RAG
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Run enhanced Rick with RAG
CMD ["python", "rick_with_rag.py"]