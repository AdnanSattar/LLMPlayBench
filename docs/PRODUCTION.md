# Production Deployment Guide for LLMPlayBench

This document provides guidelines for deploying LLMPlayBench in a production environment.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM (more for larger models)
- GPU support (optional but recommended for larger models)
- Domain name and SSL certificate (for public deployments)

## Security Considerations

Before deploying to production, make sure to:

1. **Change default credentials**:
   - Update API keys in `.env` files
   - Change the JWT secret key
   - Update the default admin credentials

2. **Configure proper CORS settings**:
   - Set `BACKEND_CORS_ORIGINS` in `backend/.env` to your frontend domain only

3. **Set up proper authentication**:
   - Consider implementing a more robust user management system
   - Implement rate limiting

4. **Protect sensitive endpoints**:
   - Ensure admin endpoints are properly secured
   - Use HTTPS for all communications

## Environment Configuration

Create a proper `.env` file for production:

```bash
# backend/.env.prod
PROJECT_NAME=LLMPlayBench
SECRET_KEY=your_secure_production_secret_key
ADMIN_API_KEY=your_secure_admin_api_key
READ_API_KEY=your_secure_read_api_key
DATABASE_URL=postgresql://user:password@postgres:5432/llm_metrics
CACHE_DIR=./models
DEFAULT_MODEL=google/flan-t5-small
MAX_NEW_TOKENS=128
REDIS_HOST=redis
REDIS_PORT=6379
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=https://your-frontend-domain.com
```

```bash
# frontend/.env.prod
VITE_API_BASE_URL=https://your-api-domain.com
VITE_API_KEY=your_secure_read_api_key
VITE_ENABLE_AUTH=true
VITE_LOG_LEVEL=info
VITE_REMOTE_LOGGING_ENABLED=true
```

## Docker Deployment

1. **Build optimized images**:

```bash
docker compose -f docker-compose.prod.yml build
```

2. **Start the services**:

```bash
docker compose -f docker-compose.prod.yml up -d
```

## Production Docker Compose File

Here's an example `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-llm_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-llm_pass}
      POSTGRES_DB: ${POSTGRES_DB:-llm_metrics}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-llm_user}"]
      interval: 10s
      retries: 5
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redisdata:/data
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    env_file:
      - ./backend/.env.prod
    volumes:
      - models_cache:/app/models
      - logs:/app/logs
    ports:
      - "127.0.0.1:8000:8000"  # Not exposed directly to the internet
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "${BACKEND_CPU_LIMIT:-2}"
          memory: "${BACKEND_MEMORY_LIMIT:-4G}"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - VITE_API_BASE_URL=${API_BASE_URL:-https://api.llmplaybench.example.com}
    ports:
      - "127.0.0.1:3000:80"  # Not exposed directly to the internet
    depends_on:
      - backend
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
  models_cache:
  logs:
```

## Optimized Backend Dockerfile

Create a `Dockerfile.prod` in the backend directory:

```dockerfile
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini
COPY ./manage_db.py /app/manage_db.py

# Create logs directory
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application with Gunicorn
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--log-level", "info", "--timeout", "120"]
```

## Optimized Frontend Dockerfile

Create a `Dockerfile.prod` in the frontend directory:

```dockerfile
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## Nginx Configuration

Create an nginx configuration for the frontend:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com;

    # Redirect all HTTP requests to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';
    
    # Frontend
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /v1/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Maintenance

### Logs

- Backend logs are stored in the `/app/logs` directory in the backend container
- Use `docker compose logs -f [service]` to view logs in real-time

### Database Maintenance

- Regularly back up the PostgreSQL database:
  ```bash
  docker compose exec postgres pg_dump -U llm_user llm_metrics > backup.sql
  ```

- Run database migrations when updating:
  ```bash
  docker compose exec backend python manage_db.py upgrade
  ```

### Scaling

- For vertical scaling, adjust the resource limits in docker-compose.yml
- For horizontal scaling, consider using Kubernetes or Docker Swarm
- When handling multiple models, consider a separate container for each model

## CI/CD Integration (GitHub Actions)

Create a `.github/workflows/deploy.yml` file:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v3
        with:
          context: ./backend
          file: ./backend/Dockerfile.prod
          push: true
          tags: yourusername/llmplaybench-backend:latest
      
      - name: Build and push frontend
        uses: docker/build-push-action@v3
        with:
          context: ./frontend
          file: ./frontend/Dockerfile.prod
          build-args: |
            VITE_API_BASE_URL=${{ secrets.API_BASE_URL }}
          push: true
          tags: yourusername/llmplaybench-frontend:latest
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/llmplaybench
            docker compose pull
            docker compose -f docker-compose.prod.yml up -d
```

## Conclusion

Following these guidelines will help you deploy LLMPlayBench securely and efficiently in a production environment. Remember to regularly update dependencies, back up your data, and monitor system performance.
