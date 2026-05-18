FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# create non-root user
RUN useradd -m appuser
WORKDIR /app

# system deps for bitsandbytes & psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mkdir -p /home/appuser/.local/bin && \
    cp /root/.local/bin/uv /home/appuser/.local/bin/ && \
    cp /root/.local/bin/uvx /home/appuser/.local/bin/ && \
    chown -R appuser:appuser /home/appuser/.local && \
    echo 'export PATH="/home/appuser/.local/bin:$PATH"' >> /home/appuser/.bashrc

# Copy project definition and README
COPY ./pyproject.toml .
COPY ../README.md .

# Generate lock file and install dependencies with uv
RUN /root/.local/bin/uv lock && \
    /root/.local/bin/uv pip install --system . && \
    /root/.local/bin/uv pip install --system --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio

# copy app and migration files
COPY ./app /app/app
COPY ./migrations /app/migrations
COPY ./alembic.ini /app/alembic.ini
COPY ./manage_db.py /app/manage_db.py
COPY .env /app/.env

# Copy and make scripts executable, ensure logs directory exists with proper permissions
COPY ./uv_manage.sh /app/uv_manage.sh
RUN chmod +x /app/manage_db.py /app/uv_manage.sh && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# chown to non-root
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
# Run migrations and start the application
CMD ["/bin/bash", "-c", "export PATH=\"/home/appuser/.local/bin:$PATH\" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]