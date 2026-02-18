# Budget Tracker API

A financial tracking application with AI optimization capabilities, built with FastAPI and SQLAlchemy. This project provides a RESTful API for managing transactions with eligibility checking for NAFFL (Not-quasi cash) benefits at UnionBank.

## Project Rationale

This budget tracker was designed to help individuals and businesses monitor their financial transactions while identifying eligible benefits under specific banking regulations. The application:

- **Real-time Eligibility Checking**: Automatically determines if transactions qualify for NAFFL benefits based on category
- **Multi-worker Support**: Designed to work with uvicorn's multi-process architecture using file-based caching
- **Async-first Architecture**: Built with FastAPI and SQLAlchemy async ORM for high performance
- **AI Optimization Ready**: Foundation laid for future AI-driven financial insights

## Features

### Core Functionality
- **Transaction Management**: Create and list transactions
- **Eligibility Checking**: Real-time determination of NAFFL eligibility
- **Caching System**: Multi-worker safe caching with configurable TTL
- **Health Monitoring**: Database connectivity health checks

### Architecture Highlights
- Async I/O throughout the stack (FastAPI, SQLAlchemy async ORM)
- Dependency injection pattern for testability
- File-based caching for multi-process worker support
- Clean domain-driven design separation

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with version info |
| GET | `/health` | Database health check |
| POST | `/transactions` | Create a new transaction |
| GET | `/transactions` | List all transactions (placeholder) |
| GET | `/eligibility/check` | Check NAFFL eligibility (cached) |
| POST | `/cache/clear` | Clear cache |
| GET | `/cache/stats` | Get cache statistics |

## Installation & Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for local development with database)
- Make (optional, for convenience commands)

### Local Development

1. Clone the repository:
```bash
git clone git@github.com:yehey123/spending-tracker.git
cd spending-tracker
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Install dependencies:
```bash
make install
# or manually: pip-sync requirements/base.txt requirements/dev.txt
```

4. Run the application:
```bash
uvicorn src.app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Docker Deployment

1. Build and start containers:
```bash
make build
make up
```

2. Access the API:
```
http://localhost:8000
```

3. Stop containers:
```bash
docker-compose down
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql+asyncpg://user:password@localhost:5432/budget_tracker | PostgreSQL connection string |
| `REDIS_URL` | redis://localhost:6379/0 | Redis URL (for future implementation) |

### Application Settings

The application can be configured through the `Settings` class in `src/app/main.py`:

- `database_pool_size`: Connection pool size (default: 10)
- `database_max_overflow`: Maximum overflow connections (default: 20)
- `cache_backend`: Cache backend type - "file" or "redis" (default: "file")
- `cache_ttl_seconds`: Cache time-to-live in seconds (default: 300)

## File-Based Caching

### Configuration
```python
# Default cache directory
CACHE_DIR = "/tmp/budget-tracker-cache"
```

The file-based cache is:
- **Process-safe**: Works correctly with uvicorn's multi-worker mode
- **Persistent**: Cache data persists across requests within the TTL window
- **Automatic cleanup**: Expired entries are automatically removed on access

### Cache Clearing
```bash
curl -X POST http://localhost:8000/cache/clear
```

### Cache Statistics
```bash
curl http://localhost:8000/cache/stats
```

Response:
```json
{
  "backend": "file",
  "cache_directory": "/tmp/budget-tracker-cache",
  "total_entries": 5,
  "total_size_bytes": 1234,
  "redis_configured": false
}
```

## Project Structure

```
spending-tracker/
├── src/
│   ├── app/
│   │   └── main.py          # FastAPI application and endpoints
│   └── domain/
│       ├── __init__.py
│       ├── models/
│       │   └── transaction.py    # Transaction model definition
│       └── services/
│           └── eligibility_service.py  # Eligibility checking logic
├── requirements/
│   ├── base.in              # Base dependencies (source)
│   ├── base.txt             # Base dependencies (compiled)
│   ├── dev.in               # Dev dependencies (source)
│   └── dev.txt              # Dev dependencies (compiled)
├── .env                     # Environment variables
├── docker-compose.yml       # Docker services definition
└── Makefile                 # Convenience commands
```

## Eligibility Rules

Transactions are marked as **eligible** for NAFFL benefits if they:
- Are NOT in "Quasi-cash" category
- Are NOT in "Cash-in" category

The eligibility check is idempotent and can be safely cached.

## Future Plans

### Redis Support
Redis integration is planned to replace the current file-based caching system. This will provide:

- Centralized cache for distributed deployments
- More sophisticated cache invalidation
- Better memory management with LRU eviction policies
- Shared cache across multiple application instances

**Status**: Design phase - Redis client integration pending

### Additional Features
- [ ] PostgreSQL database persistence with Alembic migrations
- [ ] AWS S3 integration via aioboto3 for document storage
- [ ] Real-time eligibility analytics dashboard
- [ ] Transaction categorization AI/ML model
- [ ] Export functionality (CSV, PDF)
- [ ] User authentication and authorization

## Development

### Running Tests
All 17 unit tests pass successfully.

```bash
python -m pytest tests/ -v
# or: make test (in Docker)
```

Test coverage:
- Eligibility service logic: 4 tests
- Transaction model validation: 4 tests  
- API endpoint integration: 9 tests

### Code Quality
```bash
make lint    # Run ruff linter
make hooks   # Install pre-commit hooks
```

### Dependency Management
```bash
make compile    # Compile requirements files with pip-compile
```

## License

This project is proprietary and confidential.