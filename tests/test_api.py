"""
Akura AI - API Routes Tests

Integration tests for the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_info(self, client):
        """Test that root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "modelStatus" in data or "model_status" in data


class TestAnalyzeEndpoint:
    """Tests for analyze endpoint."""
    
    def test_analyze_simple_text(self, client):
        """Test analyzing simple Sinhala text."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "මම ගෙරද යනව"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
    
    def test_analyze_empty_text_fails(self, client):
        """Test that empty text is rejected."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_includes_correct_words(self, client):
        """Test including correct words in response."""
        response = client.post(
            "/api/v1/analyze",
            json={
                "text": "මම ගෙරද යනව",
                "include_correct_words": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should include all words, including correct ones
        assert len(data["data"]) >= 1
    
    def test_analyze_returns_corrected_text(self, client):
        """Test that corrected text is returned."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": "මම ගෙරද යනව"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "correctedText" in data or "corrected_text" in data


class TestQuickCheckEndpoint:
    """Tests for quick check endpoint."""
    
    def test_quick_check_with_errors(self, client):
        """Test quick check on text with errors."""
        response = client.post(
            "/api/v1/check",
            json={"text": "මම ගෙරද යනව"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "has_errors" in data


class TestPatternsEndpoint:
    """Tests for patterns endpoint."""
    
    def test_list_patterns(self, client):
        """Test listing all dyslexia patterns."""
        response = client.get("/api/v1/patterns")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "patterns" in data
        assert len(data["patterns"]) > 0


class TestCorrectionsEndpoint:
    """Tests for corrections endpoint."""
    
    def test_list_corrections(self, client):
        """Test listing known corrections."""
        response = client.get("/api/v1/corrections")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "corrections" in data


class TestConfigEndpoint:
    """Tests for config endpoint."""
    
    def test_get_config(self, client):
        """Test getting configuration."""
        response = client.get("/api/v1/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "config" in data
        assert "model" in data["config"]


class TestBatchAnalyzeEndpoint:
    """Tests for batch analyze endpoint."""
    
    def test_batch_analyze(self, client):
        """Test batch analysis of multiple texts."""
        response = client.post(
            "/api/v1/analyze/batch",
            json={
                "texts": [
                    "මම ගෙරද යනව",
                    "මම පාසැල යනවා"
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "results" in data
        assert len(data["results"]) == 2
