"""
Test file to verify that POST methods return HTTP 201 Created status code.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime

from main import app

client = TestClient(app)


class TestPostMethodsReturn201:
    """Test class to verify POST methods return 201 Created status code"""
    
    def test_create_order_returns_201(self):
        """Test that POST /orders returns 201 Created"""
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        
        response = client.post("/orders", json=order_data)
        
        assert response.status_code == 201, \
            f"Expected 201 Created, but got {response.status_code}. Response: {response.text}"
        
        # Verify response body contains order data
        assert response.json() is not None
        assert "order_id" in response.json()
        assert response.json()["user_id"] == order_data["user_id"]
        assert response.json()["total_price"] == order_data["total_price"]
        
        # Verify Location header is present
        assert "Location" in response.headers, \
            "Location header should be present in 201 Created response"
        
        # Verify ETag header is present
        assert "ETag" in response.headers, \
            "ETag header should be present in 201 Created response"
    
    def test_create_payment_returns_201(self):
        """Test that POST /payments returns 201 Created"""
        # First create an order to reference
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        order_response = client.post("/orders", json=order_data)
        order_id = order_response.json()["order_id"]
        
        # Create payment
        payment_data = {
            "order_id": order_id,
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }
        
        response = client.post("/payments", json=payment_data)
        
        assert response.status_code == 201, \
            f"Expected 201 Created, but got {response.status_code}. Response: {response.text}"
        
        # Verify response body contains payment data
        assert response.json() is not None
        assert "payment_id" in response.json()
        assert response.json()["order_id"] == order_id
        assert response.json()["payment_method"] == payment_data["payment_method"]
        assert response.json()["amount"] == payment_data["amount"]
        
        # Verify Location header is present
        assert "Location" in response.headers, \
            "Location header should be present in 201 Created response"
        
        # Verify ETag header is present
        assert "ETag" in response.headers, \
            "ETag header should be present in 201 Created response"
    
    def test_create_order_detail_returns_201(self):
        """Test that POST /order-details returns 201 Created"""
        # First create an order to reference
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        order_response = client.post("/orders", json=order_data)
        order_id = order_response.json()["order_id"]
        
        # Create order detail
        order_detail_data = {
            "order_id": order_id,
            "prod_id": str(uuid4()),
            "quantity": 2,
            "subtotal": 199.98
        }
        
        response = client.post("/order-details", json=order_detail_data)
        
        assert response.status_code == 201, \
            f"Expected 201 Created, but got {response.status_code}. Response: {response.text}"
        
        # Verify response body contains order detail data
        assert response.json() is not None
        assert response.json()["order_id"] == order_id
        assert response.json()["prod_id"] == order_detail_data["prod_id"]
        assert response.json()["quantity"] == order_detail_data["quantity"]
        assert response.json()["subtotal"] == order_detail_data["subtotal"]
        
        # Verify Location header is present
        assert "Location" in response.headers, \
            "Location header should be present in 201 Created response"
        
        # Verify ETag header is present
        assert "ETag" in response.headers, \
            "ETag header should be present in 201 Created response"
    
    def test_all_post_endpoints_return_201(self):
        """Comprehensive test to verify all POST endpoints return 201"""
        # Test Order POST
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 100.00,
            "status": "pending"
        }
        order_response = client.post("/orders", json=order_data)
        assert order_response.status_code == 201, \
            f"POST /orders returned {order_response.status_code}, expected 201"
        
        order_id = order_response.json()["order_id"]
        prod_id = str(uuid4())
        
        # Test Payment POST
        payment_data = {
            "order_id": order_id,
            "payment_method": "paypal",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 100.00
        }
        payment_response = client.post("/payments", json=payment_data)
        assert payment_response.status_code == 201, \
            f"POST /payments returned {payment_response.status_code}, expected 201"
        
        # Test Order Detail POST
        order_detail_data = {
            "order_id": order_id,
            "prod_id": prod_id,
            "quantity": 1,
            "subtotal": 100.00
        }
        order_detail_response = client.post("/order-details", json=order_detail_data)
        assert order_detail_response.status_code == 201, \
            f"POST /order-details returned {order_detail_response.status_code}, expected 201"
        
        # Summary assertion
        assert all([
            order_response.status_code == 201,
            payment_response.status_code == 201,
            order_detail_response.status_code == 201
        ]), "All POST endpoints should return 201 Created status code"

