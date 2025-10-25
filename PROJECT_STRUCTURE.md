# Project Structure

## Directory Tree

```
onetoolsbox-be/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   │
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── v1/                   # API version 1
│   │       ├── __init__.py
│   │       └── routers/          # API route handlers
│   │           ├── __init__.py
│   │           ├── captions.py   # Caption extraction endpoints
│   │           └── health.py     # Health check endpoints
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Application configuration
│   │   └── logging_config.py    # Logging setup
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic schemas
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   └── youtube_caption_service.py
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_captions.py
│
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore patterns
├── pytest.ini                    # Pytest configuration
├── QUICKSTART.md                # Quick start guide
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
├── run.sh                        # Development run script
├── run_prod.sh                   # Production run script
└── PROJECT_STRUCTURE.md         # This file
```

## Architecture Overview

### Layer-Based Architecture

```
┌─────────────────────────────────────┐
│         API Layer (Routers)         │  ← HTTP requests/responses
├─────────────────────────────────────┤
│       Business Logic (Services)     │  ← Core functionality
├─────────────────────────────────────┤
│    Data Models (Pydantic Schemas)   │  ← Validation & serialization
├─────────────────────────────────────┤
│      Core (Config, Logging)         │  ← Infrastructure
└─────────────────────────────────────┘
```

## File Descriptions

### Application Entry Point

- **`app/main.py`**: FastAPI application initialization, middleware setup, exception handlers, and router registration

### API Layer (`app/api/v1/routers/`)

- **`captions.py`**: Endpoints for caption extraction
  - `POST /api/v1/captions/extract` - Extract clean captions
  - `POST /api/v1/captions/extract/detailed` - Extract detailed captions with timestamps

- **`health.py`**: Health check endpoints
  - `GET /health` - Health check
  - `GET /` - API info

### Core (`app/core/`)

- **`config.py`**: Application configuration using Pydantic Settings
  - Environment variable management
  - Configuration validation
  - Default values

- **`logging_config.py`**: Logging configuration
  - JSON formatter for structured logging
  - Console formatter for development
  - Logger setup and initialization

### Models (`app/models/`)

- **`schemas.py`**: Pydantic models for request/response validation
  - `CaptionRequest` - Input validation
  - `CaptionResponse` - Output formatting
  - `CaptionDetailedResponse` - Detailed output
  - `ErrorResponse` - Error formatting
  - `HealthResponse` - Health check response

### Services (`app/services/`)

- **`youtube_caption_service.py`**: Core business logic
  - Video information extraction
  - Caption extraction (VTT, SRV, JSON3 formats)
  - Caption parsing and cleaning
  - Text deduplication

### Utilities (`app/utils/`)

- **`helpers.py`**: Utility functions
  - Video ID extraction
  - Duration formatting
  - Filename sanitization
  - Text truncation

### Tests (`tests/`)

- **`test_captions.py`**: API endpoint tests
  - Health check tests
  - Validation tests
  - Integration test structure

### Configuration Files

- **`.env.example`**: Example environment variables
- **`.gitignore`**: Files to ignore in version control
- **`pytest.ini`**: Pytest configuration
- **`requirements.txt`**: Python package dependencies

### Documentation

- **`README.md`**: Comprehensive project documentation
- **`QUICKSTART.md`**: Quick start guide
- **`PROJECT_STRUCTURE.md`**: This file

### Scripts

- **`run.sh`**: Development server startup script
- **`run_prod.sh`**: Production server startup script

## API Endpoints

### Caption Extraction

```
POST /api/v1/captions/extract
POST /api/v1/captions/extract/detailed
```

### System

```
GET /health
GET /
```

## Design Patterns

### 1. Layered Architecture
- Clear separation between API, business logic, and data layers
- Each layer has specific responsibilities

### 2. Dependency Injection
- Configuration injected via environment variables
- Services can be easily mocked for testing

### 3. Factory Pattern
- Service methods are static, acting as factories
- No state maintained in service classes

### 4. Strategy Pattern
- Multiple caption format parsers (VTT, SRV, JSON3)
- Selected based on available format

### 5. Single Responsibility Principle
- Each module has one clear purpose
- Easy to maintain and test

## Data Flow

### Caption Extraction Flow

```
1. Client Request
   ↓
2. API Router (captions.py)
   ↓
3. Request Validation (schemas.py)
   ↓
4. Service Layer (youtube_caption_service.py)
   ↓
5. External API (yt-dlp → YouTube)
   ↓
6. Caption Parsing
   ↓
7. Caption Cleaning
   ↓
8. Response Formatting
   ↓
9. Client Response
```

## Extension Points

### Adding New Caption Formats

1. Add parser method in `youtube_caption_service.py`:
   ```python
   @staticmethod
   def _parse_new_format_captions(content: str) -> List[Dict]:
       # Implementation
   ```

2. Update format detection in `extract_captions()`

### Adding New Endpoints

1. Create router in `app/api/v1/routers/`
2. Add schemas in `app/models/schemas.py`
3. Register router in `app/main.py`

### Adding Middleware

Add in `app/main.py`:
```python
app.add_middleware(YourMiddleware, option=value)
```

### Adding Background Tasks

Use FastAPI's BackgroundTasks:
```python
from fastapi import BackgroundTasks

@router.post("/endpoint")
async def endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_function, arg1, arg2)
```

## Environment Variables

See `.env.example` for all available configuration options:

- Application settings (name, version, debug mode)
- API configuration (prefix, CORS)
- Logging settings (level, format)
- YouTube settings (max duration, formats)
- Rate limiting (for future implementation)

## Dependencies

Main dependencies:
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **yt-dlp**: YouTube caption extraction
- **requests**: HTTP client

See `requirements.txt` for complete list with versions.

## Testing Strategy

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints
- **Validation Tests**: Test request/response validation

Run tests:
```bash
pytest
pytest --cov=app
```

## Logging

Two logging formats available:

### JSON (Production)
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "INFO",
  "message": "Request received",
  "module": "captions"
}
```

### Console (Development)
```
2024-01-01 00:00:00 - INFO - Request received
```

## Security Considerations

- Input validation via Pydantic
- URL validation for YouTube URLs
- No sensitive data in logs
- Environment-based configuration
- CORS configuration
- Request size limits (future)
- Rate limiting (future)

## Performance Considerations

- Async/await for I/O operations
- Multiple workers in production
- Efficient caption parsing
- Text deduplication
- Connection pooling (requests)

## Deployment Options

1. **Direct**: `uvicorn app.main:app`
2. **With Gunicorn**: `gunicorn -k uvicorn.workers.UvicornWorker`
3. **Systemd**: See README.md
4. **Docker**: Future implementation

## Monitoring

Recommended monitoring points:
- Health check endpoint (`/health`)
- Request/response times
- Error rates
- Caption extraction success rates
- YouTube API availability

## Future Enhancements

- [ ] Docker containerization
- [ ] Redis caching
- [ ] Database for request history
- [ ] WebSocket support for real-time updates
- [ ] Multiple language support
- [ ] SRT file download
- [ ] Batch processing
- [ ] Rate limiting implementation
- [ ] API authentication
- [ ] Metrics endpoint

