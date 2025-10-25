# Quick Start Guide

Get the YouTube Caption Extractor API up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection

## Installation Steps

### 1. Navigate to the project directory

```bash
cd onetoolsbox-be
```

### 2. Run the setup script (Recommended)

```bash
./run.sh
```

This script will:
- Create a virtual environment
- Install all dependencies
- Create a .env file
- Start the development server

### 3. Manual Installation (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv youtubev

# Activate virtual environment
source youtubev/bin/activate  # On macOS/Linux
# OR
youtubev\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run the application
uvicorn app.main:app --reload
```

## Verify Installation

Once the server is running, open your browser and visit:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Test the API

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click on "POST /api/v1/captions/extract"
3. Click "Try it out"
4. Enter a YouTube URL:
   ```json
   {
     "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
     "format": "txt"
   }
   ```
5. Click "Execute"

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/captions/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "txt"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/captions/extract",
    json={
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "format": "txt"
    }
)

print(response.json())
```

## Common Issues

### Port already in use

If port 8000 is already in use:

```bash
uvicorn app.main:app --reload --port 8001
```

### Virtual environment not activating

Make sure you're in the project directory and try:

```bash
source ./youtubev/bin/activate
```

### Dependencies installation fails

Update pip first:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### YouTube video has no captions

Not all videos have captions. Try a different video or check if the video has English captions available on YouTube.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Check the configuration options in `.env`
- Review the code structure in the `app/` directory

## Production Deployment

For production deployment:

```bash
# Make sure DEBUG=False in .env
./run_prod.sh
```

Or use the full command:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Need Help?

- Check the [README.md](README.md) for comprehensive documentation
- Review the API docs at http://localhost:8000/docs
- Look at example requests in the documentation

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Clean Up

To deactivate the virtual environment:

```bash
deactivate
```

To remove the virtual environment completely:

```bash
rm -rf youtubev
```

