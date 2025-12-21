"""
Test file to verify correct implementation of query parameters for all collection resources.

This test suite ensures that query parameters work correctly for:
- GET /orders
- GET /payments
- GET /order-details
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, timedelta

from main import app

client = TestClient(app)


class TestOrdersQueryParameters:
    """Test query parameters for GET /orders"""
    
    def setup_method(self):
        """Set up test data before each test"""
        # Create multiple orders with different attributes for testing
        self.user_id_1 = str(uuid4())
        self.user_id_2 = str(uuid4())
        
        # Create orders with different statuses
        self.order1 = client.post("/orders", json={
            "user_id": self.user_id_1,
            "total_price": 100.00,
            "status": "pending"
        }).json()
        
        self.order2 = client.post("/orders", json={
            "user_id": self.user_id_1,
            "total_price": 200.00,
            "status": "shipped"
        }).json()
        
        self.order3 = client.post("/orders", json={
            "user_id": self.user_id_2,
            "total_price": 300.00,
            "status": "pending"
        }).json()
        
        self.order4 = client.post("/orders", json={
            "user_id": self.user_id_2,
            "total_price": 400.00,
            "status": "delivered"
        }).json()
    
    def test_get_orders_without_parameters_returns_all(self):
        """Test that GET /orders without parameters returns all orders"""
        response = client.get("/orders")
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        assert len(orders) >= 4
    
    def test_get_orders_filter_by_user_id(self):
        """Test filtering orders by user_id"""
        response = client.get(f"/orders?user_id={self.user_id_1}")
        assert response.status_code == 200
        orders = response.json()
        assert all(order["user_id"] == self.user_id_1 for order in orders)
    
    def test_get_orders_filter_by_status(self):
        """Test filtering orders by status"""
        response = client.get("/orders?status=pending")
        assert response.status_code == 200
        orders = response.json()
        assert all(order["status"] == "pending" for order in orders)
        
        response = client.get("/orders?status=shipped")
        assert response.status_code == 200
        orders = response.json()
        assert all(order["status"] == "shipped" for order in orders)
    
    def test_get_orders_filter_by_min_total_price(self):
        """Test filtering orders by min_total_price"""
        response = client.get("/orders?min_total_price=250.00")
        assert response.status_code == 200
        orders = response.json()
        assert all(order["total_price"] >= 250.00 for order in orders)
    
    def test_get_orders_filter_by_max_total_price(self):
        """Test filtering orders by max_total_price"""
        response = client.get("/orders?max_total_price=250.00")
        assert response.status_code == 200
        orders = response.json()
        assert all(order["total_price"] <= 250.00 for order in orders)
    
    def test_get_orders_filter_by_price_range(self):
        """Test filtering orders by min and max total_price"""
        response = client.get("/orders?min_total_price=150.00&max_total_price=350.00")
        assert response.status_code == 200
        orders = response.json()
        assert all(150.00 <= order["total_price"] <= 350.00 for order in orders)
    
    def test_get_orders_pagination_with_limit(self):
        """Test pagination with limit parameter"""
        response = client.get("/orders?limit=2")
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) <= 2
    
    def test_get_orders_pagination_with_offset(self):
        """Test pagination with offset parameter"""
        # Get first page
        response1 = client.get("/orders?limit=2")
        assert response1.status_code == 200
        orders1 = response1.json()
        
        # Get second page
        response2 = client.get("/orders?limit=2&offset=2")
        assert response2.status_code == 200
        orders2 = response2.json()
        
        # Results should be different
        if len(orders1) == 2 and len(orders2) > 0:
            assert orders1[0]["order_id"] != orders2[0]["order_id"]
    
    def test_get_orders_invalid_limit(self):
        """Test that invalid limit (less than 1) returns validation error"""
        response = client.get("/orders?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_get_orders_invalid_offset(self):
        """Test that invalid offset (less than 0) returns validation error"""
        response = client.get("/orders?offset=-1")
        assert response.status_code == 422  # Validation error


class TestPaymentsQueryParameters:
    """Test query parameters for GET /payments"""
    
    def setup_method(self):
        """Set up test data before each test"""
        # Create orders first
        self.order1 = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 100.00,
            "status": "pending"
        }).json()
        
        self.order2 = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 200.00,
            "status": "pending"
        }).json()
        
        # Create payments with different attributes
        now = datetime.utcnow()
        self.payment1 = client.post("/payments", json={
            "order_id": self.order1["order_id"],
            "payment_method": "credit_card",
            "payment_date": now.isoformat() + "Z",
            "amount": 100.00
        }).json()
        
        self.payment2 = client.post("/payments", json={
            "order_id": self.order1["order_id"],
            "payment_method": "paypal",
            "payment_date": (now + timedelta(days=1)).isoformat() + "Z",
            "amount": 200.00
        }).json()
        
        self.payment3 = client.post("/payments", json={
            "order_id": self.order2["order_id"],
            "payment_method": "credit_card",
            "payment_date": (now + timedelta(days=2)).isoformat() + "Z",
            "amount": 150.00
        }).json()
    
    def test_get_payments_without_parameters_returns_all(self):
        """Test that GET /payments without parameters returns all payments"""
        response = client.get("/payments")
        assert response.status_code == 200
        payments = response.json()
        assert isinstance(payments, list)
        assert len(payments) >= 3
    
    def test_get_payments_filter_by_order_id(self):
        """Test filtering payments by order_id"""
        response = client.get(f"/payments?order_id={self.order1['order_id']}")
        assert response.status_code == 200
        payments = response.json()
        assert all(payment["order_id"] == self.order1["order_id"] for payment in payments)
    
    def test_get_payments_filter_by_payment_method(self):
        """Test filtering payments by payment_method"""
        response = client.get("/payments?payment_method=credit_card")
        assert response.status_code == 200
        payments = response.json()
        assert all(payment["payment_method"] == "credit_card" for payment in payments)
    
    def test_get_payments_filter_by_min_amount(self):
        """Test filtering payments by min_amount"""
        response = client.get("/payments?min_amount=150.00")
        assert response.status_code == 200
        payments = response.json()
        assert all(payment["amount"] >= 150.00 for payment in payments)
    
    def test_get_payments_filter_by_max_amount(self):
        """Test filtering payments by max_amount"""
        response = client.get("/payments?max_amount=150.00")
        assert response.status_code == 200
        payments = response.json()
        assert all(payment["amount"] <= 150.00 for payment in payments)
    
    def test_get_payments_filter_by_amount_range(self):
        """Test filtering payments by min and max amount"""
        response = client.get("/payments?min_amount=120.00&max_amount=180.00")
        assert response.status_code == 200
        payments = response.json()
        assert all(120.00 <= payment["amount"] <= 180.00 for payment in payments)
    
    def test_get_payments_pagination_with_limit(self):
        """Test pagination with limit parameter"""
        response = client.get("/payments?limit=2")
        assert response.status_code == 200
        payments = response.json()
        assert len(payments) <= 2


class TestOrderDetailsQueryParameters:
    """Test query parameters for GET /order-details"""
    
    def setup_method(self):
        """Set up test data before each test"""
        # Create an order first
        self.order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 500.00,
            "status": "pending"
        }).json()
        
        self.prod_id_1 = str(uuid4())
        self.prod_id_2 = str(uuid4())
        
        # Create order details with different attributes
        self.order_detail1 = client.post("/order-details", json={
            "order_id": self.order["order_id"],
            "prod_id": self.prod_id_1,
            "quantity": 2,
            "subtotal": 100.00
        }).json()
        
        self.order_detail2 = client.post("/order-details", json={
            "order_id": self.order["order_id"],
            "prod_id": self.prod_id_2,
            "quantity": 5,
            "subtotal": 250.00
        }).json()
    
    def test_get_order_details_without_parameters_returns_all(self):
        """Test that GET /order-details without parameters returns all order details"""
        response = client.get("/order-details")
        assert response.status_code == 200
        order_details = response.json()
        assert isinstance(order_details, list)
        assert len(order_details) >= 2
    
    def test_get_order_details_filter_by_order_id(self):
        """Test filtering order details by order_id"""
        response = client.get(f"/order-details?order_id={self.order['order_id']}")
        assert response.status_code == 200
        order_details = response.json()
        assert all(detail["order_id"] == self.order["order_id"] for detail in order_details)
    
    def test_get_order_details_filter_by_prod_id(self):
        """Test filtering order details by prod_id"""
        response = client.get(f"/order-details?prod_id={self.prod_id_1}")
        assert response.status_code == 200
        order_details = response.json()
        assert all(detail["prod_id"] == self.prod_id_1 for detail in order_details)
    
    def test_get_order_details_filter_by_min_quantity(self):
        """Test filtering order details by min_quantity"""
        response = client.get("/order-details?min_quantity=3")
        assert response.status_code == 200
        order_details = response.json()
        assert all(detail["quantity"] >= 3 for detail in order_details)
    
    def test_get_order_details_filter_by_max_quantity(self):
        """Test filtering order details by max_quantity"""
        response = client.get("/order-details?max_quantity=3")
        assert response.status_code == 200
        order_details = response.json()
        assert all(detail["quantity"] <= 3 for detail in order_details)
    
    def test_get_order_details_filter_by_min_subtotal(self):
        """Test filtering order details by min_subtotal"""
        response = client.get("/order-details?min_subtotal=150.00")
        assert response.status_code == 200
        order_details = response.json()
        assert all(detail["subtotal"] >= 150.00 for detail in order_details)
    
    def test_get_order_details_filter_by_max_subtotal(self):
        """Test filtering order details by max_subtotal"""
        response = client.get("/order-details?max_subtotal=150.00")
        assert response.status_code == 200
        order_details = response.json()
        assert all(detail["subtotal"] <= 150.00 for detail in order_details)
    
    def test_get_order_details_sort_by_quantity_asc(self):
        """Test sorting order details by quantity in ascending order"""
        response = client.get("/order-details?sort_by=quantity&order=asc")
        assert response.status_code == 200
        order_details = response.json()
        quantities = [detail["quantity"] for detail in order_details]
        assert quantities == sorted(quantities)
    
    def test_get_order_details_sort_by_subtotal_desc(self):
        """Test sorting order details by subtotal in descending order"""
        response = client.get("/order-details?sort_by=subtotal&order=desc")
        assert response.status_code == 200
        order_details = response.json()
        subtotals = [detail["subtotal"] for detail in order_details]
        assert subtotals == sorted(subtotals, reverse=True)
    
    def test_get_order_details_pagination_with_limit(self):
        """Test pagination with limit parameter"""
        response = client.get("/order-details?limit=1")
        assert response.status_code == 200
        order_details = response.json()
        assert len(order_details) <= 1
