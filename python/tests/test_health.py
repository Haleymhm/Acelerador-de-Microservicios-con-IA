"""Tests for the health check endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    """GET /api/v1/health should return status ok."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "risk-analysis-accelerator"


def test_health_response_structure(client: TestClient) -> None:
    """Health response should contain exactly 'status' and 'service' keys."""
    response = client.get("/api/v1/health")
    data = response.json()

    assert set(data.keys()) == {"status", "service"}
