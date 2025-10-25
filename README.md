# YouTube Caption Extractor API

A production-ready FastAPI application for extracting and processing captions from YouTube videos.

## Features

- 🎬 Extract captions from YouTube videos
- 📝 Support for multiple caption formats (VTT, SRV3, JSON3)
- 🧹 Clean and deduplicate caption text
- ⏱️ Get detailed captions with timestamps
- 📊 RESTful API with comprehensive documentation
- 🔒 Production-ready with proper error handling
- 📝 Structured logging (JSON/Console)
- ⚡ Fast and async
- 🔧 Configurable via environment variables

## Tech Stack

- **Framework**: FastAPI
- **Python**: 3.8+
- **Caption Extraction**: yt-dlp
- **Server**: Uvicorn/Gunicorn
- **Validation**: Pydantic v2

## Project Structure

```
onetoolsbox-be/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/
│   │           ├── __init__.py
│   │           ├── captions.py  # Caption endpoints
│   │           └── health.py    # Health check
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   └── logging_config.py   # Logging setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── youtube_caption_service.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # Utility functions
├── tests/                      # Test files
├── .env.example               # Example environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd onetoolsbox-be
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv youtubev

# Activate virtual environment
# On macOS/Linux:
source youtubev/bin/activate

# On Windows:
youtubev\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

## Configuration

Edit the `.env` file to customize the application:

```env
# Application
APP_NAME="YouTube Caption Extractor API"
DEBUG=False

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"  # or "console"

# YouTube Settings
MAX_VIDEO_DURATION=7200  # 2 hours

# CORS
ALLOWED_ORIGINS="*"  # Use specific domains in production
```

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source youtubev/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Using Python directly

```bash
python -m app.main
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Extract Captions (Clean Text)

```bash
POST /api/v1/captions/extract
Content-Type: application/json

{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "format": "txt"
}
```

Response:
```json
{
  "success": true,
  "video_title": "Sample Video Title",
  "video_id": "VIDEO_ID",
  "caption_format": "vtt",
  "clean_text": "This is the cleaned caption text...",
  "content_length": 1250
}
```

### Extract Detailed Captions (With Timestamps)

```bash
POST /api/v1/captions/extract/detailed
Content-Type: application/json

{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "format": "txt"
}
```

Response:
```json
{
  "success": true,
  "video_title": "Sample Video Title",
  "video_id": "VIDEO_ID",
  "video_duration": 300.5,
  "total_captions": 150,
  "format": "vtt",
  "captions": [
    {
      "start_time": 0.0,
      "end_time": 2.5,
      "duration": 2.5,
      "text": "Hello and welcome..."
    }
  ]
}
```

## Usage Examples

### Using cURL

```bash
# Extract clean captions
curl -X POST "http://localhost:8000/api/v1/captions/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "txt"
  }'

# Extract detailed captions
curl -X POST "http://localhost:8000/api/v1/captions/extract/detailed" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "txt"
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/v1/captions/extract"
payload = {
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "txt"
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Video: {data['video_title']}")
print(f"Captions: {data['clean_text'][:100]}...")
```

### Using JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/captions/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    youtube_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    format: 'txt'
  })
});

const data = await response.json();
console.log('Video:', data.video_title);
console.log('Captions:', data.clean_text);
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

```json
{
  "detail": {
    "success": false,
    "error": "Failed to extract captions",
    "details": "No English captions available for this video"
  }
}
```

Common error codes:
- `400`: Bad Request (invalid URL, no captions available)
- `422`: Validation Error (invalid request format)
- `500`: Internal Server Error

## Logging

The application uses structured logging with two formats:

### JSON Logging (Production)
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "level": "INFO",
  "message": "Extracting captions from: ...",
  "module": "youtube_caption_service"
}
```

### Console Logging (Development)
```
2024-01-01 00:00:00 - onetoolsbox - INFO - Extracting captions from: ...
```

Configure logging in `.env`:
```env
LOG_LEVEL="INFO"    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT="json"   # json or console
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_captions.py
```

## Production Deployment

### Best Practices

1. **Environment Variables**: Use proper environment variables for production
   ```env
   DEBUG=False
   LOG_LEVEL="WARNING"
   ALLOWED_ORIGINS="https://yourdomain.com"
   ```

2. **Workers**: Use multiple workers for better performance
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Reverse Proxy**: Use Nginx or similar as a reverse proxy

4. **HTTPS**: Always use HTTPS in production

5. **Rate Limiting**: Consider implementing rate limiting for API endpoints

6. **Monitoring**: Set up logging aggregation and monitoring

### Using Gunicorn

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Using systemd (Linux)

Create `/etc/systemd/system/onetoolsbox.service`:

```ini
[Unit]
Description=YouTube Caption Extractor API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/onetoolsbox-be
Environment="PATH=/path/to/onetoolsbox-be/youtubev/bin"
ExecStart=/path/to/onetoolsbox-be/youtubev/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl start onetoolsbox
sudo systemctl enable onetoolsbox
```

## Troubleshooting

### Common Issues

1. **No captions available**
   - Not all YouTube videos have captions
   - Check if the video has English captions available

2. **Rate limiting from YouTube**
   - yt-dlp may be rate-limited by YouTube
   - Consider implementing caching or request throttling

3. **Long video processing**
   - Videos longer than 2 hours are rejected by default
   - Adjust `MAX_VIDEO_DURATION` in `.env` if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`

## Changelog

### v1.0.0 (2024-01-01)
- Initial release
- Basic caption extraction
- Clean and detailed endpoints
- Production-ready structure

