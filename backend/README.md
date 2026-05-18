# LLMPlayBench Backend

Backend API service for LLMPlayBench, providing OpenAI-compatible inference endpoints for small language models.

## Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   │   ├── endpoints/    # API endpoint implementations
│   │   └── router.py     # Main API router
│   ├── core/             # Core application components
│   │   ├── config.py     # Application configuration
│   │   └── security/     # Authentication and security
│   ├── models/           # Model definitions and wrappers
│   ├── schemas/          # Pydantic schemas and DB models
│   │   ├── api_schemas.py  # API request/response schemas
│   │   └── db_models.py    # SQLAlchemy ORM models
│   ├── services/         # Business logic services
│   │   ├── benchmark_service.py   # Model benchmarking
│   │   ├── db_service.py          # Database operations
│   │   ├── metrics_service.py     # Metrics collection
│   │   └── model_service.py       # Model management
│   └── main.py           # FastAPI application entry point
├── migrations/           # Alembic database migrations
│   ├── versions/         # Migration script versions
│   ├── env.py            # Migration environment configuration
│   └── README            # Migration documentation
├── .env                  # Environment variables
├── alembic.ini           # Alembic configuration
├── Dockerfile            # Container definition
├── manage_db.py          # Database management script
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Core Endpoints

- **GET /health**: Health check endpoint
- **POST /v1/response**: Generate text from a model
- **GET /v1/models**: List available models
- **GET /v1/benchmarks**: Benchmark a specific model

### Metrics Endpoints (Authenticated)

- **GET /v1/metrics/recent**: Get recent request metrics
- **POST /v1/metrics/recent**: Filter metrics by criteria
- **GET /v1/metrics/summary**: Get aggregated metrics

### Admin Endpoints (Admin Authentication Required)

- **POST /v1/admin/reload_model**: Reload a specific model
- **DELETE /v1/admin/unload_model**: Unload a specific model

### Authentication Endpoints

- **POST /v1/auth/token**: Get JWT access token
- **GET /v1/auth/me**: Get current user information
- **GET /v1/auth/status**: Check authentication status

## Authentication

The API supports two authentication methods:

- **API Keys**: Send via `X-API-Key` header
- **JWT Tokens**: Send via `Authorization: Bearer <token>` header

## Database Migrations

Migrations are managed using Alembic:

```bash
# Install dependencies
./uv_manage.sh install

# Apply migrations
python manage_db.py upgrade

# Run the application
./uv_manage.sh run

# Show migration history
python manage_db.py history
```

## Run the application

```shell
uvicorn app.main:app --reload
```

## Environment Variables

See `.env` file for configuration options, including:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `ADMIN_API_KEY`: Admin API key
- `READ_API_KEY`: Read-only API key

## Author

Adnan Sattar

- Email: <adnansattar09@gmail.com>
- GitHub: <https://github.com/AdnanSattar>
- LinkedIn: <https://www.linkedin.com/in/adnansattar09/>