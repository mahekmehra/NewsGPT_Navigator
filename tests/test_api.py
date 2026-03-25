"""
Tests for the FastAPI backend.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_health_check():
    """Health endpoint should return ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["agents"]) >= 5


def test_get_languages():
    """Languages endpoint should return supported languages."""
    response = client.get("/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    codes = [lang["code"] for lang in data["languages"]]
    assert "en" in codes
    assert "hi" in codes


def test_get_personas():
    """Personas endpoint should return available personas."""
    response = client.get("/personas")
    assert response.status_code == 200
    data = response.json()
    assert "personas" in data
    names = [p["name"] for p in data["personas"]]
    assert "General" in names
    assert "Student" in names
    assert "Investor" in names


def test_get_sessions_empty():
    """Sessions endpoint should return empty list initially."""
    response = client.get("/sessions")
    assert response.status_code == 200


def test_audit_not_found():
    """Audit endpoint should 404 for unknown session."""
    response = client.get("/audit/nonexistent-id")
    assert response.status_code == 404
