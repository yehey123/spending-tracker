import pytest
from fastapi.testclient import TestClient

from src.app.main import app


class TestMainEndpoints:
    def setup_method(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        assert app.title == "Budget Tracker API"
        assert app.version == "0.1.0"

    def test_health_check_database_connection(self):
        response = self.client.get("/health")
        
        assert response.status_code in [200, 503]

    def test_create_transaction_endpoint(self):
        transaction_data = {
            "description": "Test purchase",
            "amount": "100.00",
            "category": "Groceries",
        }
        
        response = self.client.post("/transactions", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Test purchase"
        assert data["amount"] == "100.00"
        assert data["category"] == "Groceries"

    def test_create_transaction_ineligible_category(self):
        transaction_data = {
            "description": "Gift card",
            "amount": "50.00",
            "category": "Quasi-cash",
        }
        
        response = self.client.post("/transactions", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_naffl_eligible"] is False

    def test_create_transaction_eligible_category(self):
        transaction_data = {
            "description": "Grocery shopping",
            "amount": "150.00",
            "category": "Food",
        }
        
        response = self.client.post("/transactions", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_naffl_eligible"] is True

    def test_list_transactions_endpoint(self):
        response = self.client.get("/transactions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_eligibility_check_endpoint(self):
        response = self.client.get(
            "/eligibility/check",
            params={
                "description": "Test purchase",
                "amount": 100.00,
                "category": "Groceries",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "transaction" in data
        assert "is_eligible" in data
        assert data["is_eligible"] is True

    def test_cache_clear_endpoint(self):
        response = self.client.post("/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cache cleared successfully"

    def test_cache_stats_endpoint(self):
        response = self.client.get("/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "backend" in data
        assert "total_entries" in data
