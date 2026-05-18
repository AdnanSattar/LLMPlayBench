"""
API Tests for LLMPlayBench.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import os

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test API keys
READ_API_KEY = os.environ.get("READ_API_KEY", "read-dev-key")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "admin-dev-key")


def test_health_endpoint():
    """Test that the health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_without_auth():
    """Test that the metrics endpoint requires authentication."""
    response = client.get("/v1/metrics/recent")
    assert response.status_code == 401


def test_metrics_endpoint_with_read_key():
    """Test that the metrics endpoint works with read API key."""
    headers = {"X-API-Key": READ_API_KEY}
    response = client.get("/v1/metrics/recent", headers=headers)
    assert response.status_code == 200
    assert "metrics" in response.json()


def test_metrics_summary_endpoint():
    """Test that the metrics summary endpoint works with read API key."""
    headers = {"X-API-Key": READ_API_KEY}
    response = client.get("/v1/metrics/summary", headers=headers)
    assert response.status_code == 200


def test_models_endpoint():
    """Test that the models endpoint works with read API key."""
    headers = {"X-API-Key": READ_API_KEY}
    response = client.get("/v1/models", headers=headers)
    assert response.status_code == 200
    # Even if no models are loaded, it should return a list
    assert isinstance(response.json(), list)


def test_admin_endpoint_with_read_key():
    """Test that admin endpoints reject read API key."""
    headers = {"X-API-Key": READ_API_KEY}
    response = client.get("/v1/auth/admin", headers=headers)
    assert response.status_code == 403  # Forbidden


def test_admin_endpoint_with_admin_key():
    """Test that admin endpoints accept admin API key."""
    headers = {"X-API-Key": ADMIN_API_KEY}
    response = client.get("/v1/auth/admin", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


if __name__ == "__main__":
    # Simple test runner for manual execution
    test_health_endpoint()
    test_metrics_endpoint_without_auth()
    test_metrics_endpoint_with_read_key()
    test_metrics_summary_endpoint()
    test_models_endpoint()
    test_admin_endpoint_with_read_key()
    test_admin_endpoint_with_admin_key()
    print("All tests passed!")
