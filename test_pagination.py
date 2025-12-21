"""
Test file to verify correct implementation of pagination for collection resources.
This test suite focuses on pagination functionality for GET /orders endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app

client = TestClient(app)


class TestPaginationOrders:
    """Test pagination for GET /orders endpoint"""
    
    def setup_method(self):
        """Set up test data: create multiple orders for pagination testing"""
        # Create 10 orders to test pagination thoroughly
        self.created_orders = []
        for i in range(10):
            order = client.post("/orders", json={
                "user_id": str(uuid4()),
                "total_price": 100.00 + (i * 10),
                "status": "pending"
            }).json()
            self.created_orders.append(order)
        
        # Store order IDs for verification
        self.order_ids = [order["order_id"] for order in self.created_orders]
    
    def test_get_orders_without_pagination_returns_all(self):
        """Test that GET /orders without pagination parameters returns all orders"""
        response = client.get("/orders")
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        # Should return at least our 10 test orders (may have more from other tests)
        assert len(orders) >= 10
    
    def test_get_orders_with_limit_only(self):
        """Test pagination with limit parameter only"""
        response = client.get("/orders?limit=5")
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 5, \
            f"Expected 5 orders with limit=5, but got {len(orders)}"
    
    def test_get_orders_with_limit_one(self):
        """Test pagination with limit=1 (minimum valid limit)"""
        response = client.get("/orders?limit=1")
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 1, \
            f"Expected 1 order with limit=1, but got {len(orders)}"
    
    def test_get_orders_with_offset_only(self):
        """Test pagination with offset parameter only (should skip first N items)"""
        # Get all orders first
        all_orders = client.get("/orders").json()
        total_count = len(all_orders)
        
        if total_count >= 5:
            # Get orders with offset=3 (skip first 3)
            response = client.get("/orders?offset=3")
            assert response.status_code == 200
            offset_orders = response.json()
            # Should have fewer items than total (total - offset)
            assert len(offset_orders) == total_count - 3, \
                f"Expected {total_count - 3} orders with offset=3, but got {len(offset_orders)}"
    
    def test_get_orders_with_offset_zero(self):
        """Test pagination with offset=0 (should return all items up to limit)"""
        response = client.get("/orders?offset=0&limit=5")
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 5, \
            "Offset=0 should not skip any items"
    