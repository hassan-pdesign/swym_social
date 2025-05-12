from fastapi.testclient import TestClient
import pytest
from app.api.app import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "app" in response.json()
    assert "version" in response.json()
    assert "status" in response.json()
    assert response.json()["status"] == "running"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Test content endpoints
def test_get_content_sources():
    """Test getting content sources."""
    response = client.get("/api/content/sources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_content_items():
    """Test getting content items."""
    response = client.get("/api/content/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test post endpoints
def test_get_posts():
    """Test getting posts."""
    response = client.get("/api/posts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 