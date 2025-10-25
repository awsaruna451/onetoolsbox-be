"""
Tests for caption extraction endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_extract_captions_invalid_url():
    """Test caption extraction with invalid URL"""
    response = client.post(
        "/api/v1/captions/extract",
        json={
            "youtube_url": "https://invalid-url.com",
            "format": "txt"
        }
    )
    assert response.status_code == 422  # Validation error


def test_extract_captions_missing_url():
    """Test caption extraction without URL"""
    response = client.post(
        "/api/v1/captions/extract",
        json={"format": "txt"}
    )
    assert response.status_code == 422  # Validation error


def test_extract_captions_invalid_format():
    """Test caption extraction with invalid format"""
    response = client.post(
        "/api/v1/captions/extract",
        json={
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "format": "invalid"
        }
    )
    assert response.status_code == 422  # Validation error


# Note: Add more integration tests with actual YouTube videos
# These would require network access and specific test videos
# with known captions available

