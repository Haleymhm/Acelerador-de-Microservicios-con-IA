"""Tests for the analysis API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestSubmitAnalysis:
    """Tests for POST /api/v1/analysis/analyze."""

    def test_submit_returns_202(self, client: TestClient) -> None:
        """Submitting valid text should return HTTP 202 with an analysis_id."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={
                "text": "The payment service depends on the auth module. There is a critical risk of DB migration failure.",
                "source_filename": "test-doc.md",
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert "analysis_id" in data
        assert data["status"] == "processing"

    def test_submit_rejects_short_text(self, client: TestClient) -> None:
        """Text shorter than 10 characters should be rejected with 422."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={"text": "short", "source_filename": "test.md"},
        )
        assert response.status_code == 422

    def test_submit_uses_default_filename(self, client: TestClient) -> None:
        """If source_filename is omitted, a default should be applied."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={"text": "A sufficiently long piece of text for analysis testing purposes"},
        )
        assert response.status_code == 202

    def test_submit_requires_text_field(self, client: TestClient) -> None:
        """Omitting the required 'text' field should return 422."""
        response = client.post(
            "/api/v1/analysis/analyze",
            json={"source_filename": "test.md"},
        )
        assert response.status_code == 422


class TestGetAnalysis:
    """Tests for GET /api/v1/analysis/{analysis_id}."""

    def test_unknown_id_returns_404(self, client: TestClient) -> None:
        """Querying a non-existent analysis should return 404."""
        response = client.get("/api/v1/analysis/nonexistent-id-12345")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
