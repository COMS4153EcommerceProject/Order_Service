"""
Test file to verify correct implementation of linked data and relative paths.

This test suite ensures that:
1. All resources include a "links" field in their responses
2. Links contain correct relative paths (not absolute URLs)
3. "self" links point to the resource itself
4. Related resource links are correctly formatted
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime

from main import app

client = TestClient(app)


class TestLinkedDataOrders:
    """Test linked data for Order resources"""
    
    def test_order_has_links_field(self):
        """Test that Order resource includes links field"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        
        order = response.json()
        assert "links" in order, "Order should have 'links' field"
        assert isinstance(order["links"], dict), "Links should be a dictionary"
    
    def test_order_has_self_link(self):
        """Test that Order has correct 'self' link"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        
        order = response.json()
        assert "self" in order["links"], "Order links should contain 'self'"
        
        # Verify self link format
        self_link = order["links"]["self"]
        assert self_link.startswith("/orders/"), \
            f"Self link should start with '/orders/', got: {self_link}"
        assert order["order_id"] in self_link, \
            "Self link should contain the order_id"
        assert self_link == f"/orders/{order['order_id']}", \
            f"Self link should be '/orders/{{order_id}}', got: {self_link}"
    
    def test_order_has_payments_link(self):
        """Test that Order has correct 'payments' link"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        
        order = response.json()
        assert "payments" in order["links"], "Order links should contain 'payments'"
        
        # Verify payments link format
        payments_link = order["links"]["payments"]
        assert payments_link.startswith("/payments"), \
            f"Payments link should start with '/payments', got: {payments_link}"
        assert "order_id=" in payments_link, \
            "Payments link should contain order_id query parameter"
        assert order["order_id"] in payments_link, \
            "Payments link should contain the order_id"
        assert payments_link == f"/payments?order_id={order['order_id']}", \
            f"Payments link should be '/payments?order_id={{order_id}}', got: {payments_link}"
    
    def test_order_has_order_details_link(self):
        """Test that Order has correct 'order_details' link"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        
        order = response.json()
        assert "order_details" in order["links"], \
            "Order links should contain 'order_details'"
        
        # Verify order_details link format
        order_details_link = order["links"]["order_details"]
        assert order_details_link.startswith("/order-details"), \
            f"Order details link should start with '/order-details', got: {order_details_link}"
        assert "order_id=" in order_details_link, \
            "Order details link should contain order_id query parameter"
        assert order["order_id"] in order_details_link, \
            "Order details link should contain the order_id"
        assert order_details_link == f"/order-details?order_id={order['order_id']}", \
            f"Order details link should be '/order-details?order_id={{order_id}}', got: {order_details_link}"
    
    def test_order_payments_link_is_accessible(self):
        """Test that Order payments link is accessible"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        assert create_response.status_code == 201
        
        order = create_response.json()
        payments_link = order["links"]["payments"]
        
        # Follow the payments link
        get_response = client.get(payments_link)
        assert get_response.status_code == 200, \
            f"Payments link should be accessible, got status {get_response.status_code}"
        
        payments = get_response.json()
        assert isinstance(payments, list), \
            "Payments link should return a list"
        # All payments should belong to this order (if any exist)
        for payment in payments:
            assert payment["order_id"] == order["order_id"], \
                "Payments link should return payments for this order"

class TestLinkedDataPayments:
    """Test linked data for Payment resources"""
    
    def test_payment_has_links_field(self):
        """Test that Payment resource includes links field"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create a payment
        payment_data = {
            "order_id": order["order_id"],
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }
        response = client.post("/payments", json=payment_data)
        assert response.status_code == 201
        
        payment = response.json()
        assert "links" in payment, "Payment should have 'links' field"
        assert isinstance(payment["links"], dict), "Links should be a dictionary"
    
    def test_payment_has_self_link(self):
        """Test that Payment has correct 'self' link"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create a payment
        payment_data = {
            "order_id": order["order_id"],
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }
        response = client.post("/payments", json=payment_data)
        assert response.status_code == 201
        
        payment = response.json()
        assert "self" in payment["links"], "Payment links should contain 'self'"
        
        # Verify self link format
        self_link = payment["links"]["self"]
        assert self_link.startswith("/payments/"), \
            f"Self link should start with '/payments/', got: {self_link}"
        assert payment["payment_id"] in self_link, \
            "Self link should contain the payment_id"
        assert self_link == f"/payments/{payment['payment_id']}", \
            f"Self link should be '/payments/{{payment_id}}', got: {self_link}"
    
    def test_payment_has_order_link(self):
        """Test that Payment has correct 'order' link"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create a payment
        payment_data = {
            "order_id": order["order_id"],
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }
        response = client.post("/payments", json=payment_data)
        assert response.status_code == 201
        
        payment = response.json()
        assert "order" in payment["links"], "Payment links should contain 'order'"
        
        # Verify order link format
        order_link = payment["links"]["order"]
        assert order_link.startswith("/orders/"), \
            f"Order link should start with '/orders/', got: {order_link}"
        assert payment["order_id"] in order_link, \
            "Order link should contain the order_id"
        assert order_link == f"/orders/{payment['order_id']}", \
            f"Order link should be '/orders/{{order_id}}', got: {order_link}"
    
    def test_payment_order_link_is_accessible(self):
        """Test that Payment order link is accessible (returns the order)"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create a payment
        payment_data = {
            "order_id": order["order_id"],
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }
        response = client.post("/payments", json=payment_data)
        assert response.status_code == 201
        
        payment = response.json()
        order_link = payment["links"]["order"]
        
        # Follow the order link
        get_response = client.get(order_link)
        assert get_response.status_code == 200, \
            f"Order link should be accessible, got status {get_response.status_code}"
        
        retrieved_order = get_response.json()
        assert retrieved_order["order_id"] == payment["order_id"], \
            "Order link should return the associated order"


class TestLinkedDataOrderDetails:
    """Test linked data for OrderDetail resources"""
    
    def test_order_detail_has_links_field(self):
        """Test that OrderDetail resource includes links field"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create an order detail
        order_detail_data = {
            "order_id": order["order_id"],
            "prod_id": str(uuid4()),
            "quantity": 2,
            "subtotal": 199.98
        }
        response = client.post("/order-details", json=order_detail_data)
        assert response.status_code == 201
        
        order_detail = response.json()
        assert "links" in order_detail, "OrderDetail should have 'links' field"
        assert isinstance(order_detail["links"], dict), "Links should be a dictionary"
    
    def test_order_detail_has_self_link(self):
        """Test that OrderDetail has correct 'self' link"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        prod_id = str(uuid4())
        
        # Create an order detail
        order_detail_data = {
            "order_id": order["order_id"],
            "prod_id": prod_id,
            "quantity": 2,
            "subtotal": 199.98
        }
        response = client.post("/order-details", json=order_detail_data)
        assert response.status_code == 201
        
        order_detail = response.json()
        assert "self" in order_detail["links"], "OrderDetail links should contain 'self'"
        
        # Verify self link format (composite key: order_id/prod_id)
        self_link = order_detail["links"]["self"]
        assert self_link.startswith("/order-details/"), \
            f"Self link should start with '/order-details/', got: {self_link}"
        assert order_detail["order_id"] in self_link, \
            "Self link should contain the order_id"
        assert order_detail["prod_id"] in self_link, \
            "Self link should contain the prod_id"
        assert self_link == f"/order-details/{order_detail['order_id']}/{order_detail['prod_id']}", \
            f"Self link should be '/order-details/{{order_id}}/{{prod_id}}', got: {self_link}"
    
    def test_order_detail_has_order_link(self):
        """Test that OrderDetail has correct 'order' link"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create an order detail
        order_detail_data = {
            "order_id": order["order_id"],
            "prod_id": str(uuid4()),
            "quantity": 2,
            "subtotal": 199.98
        }
        response = client.post("/order-details", json=order_detail_data)
        assert response.status_code == 201
        
        order_detail = response.json()
        assert "order" in order_detail["links"], "OrderDetail links should contain 'order'"
        
        # Verify order link format
        order_link = order_detail["links"]["order"]
        assert order_link.startswith("/orders/"), \
            f"Order link should start with '/orders/', got: {order_link}"
        assert order_detail["order_id"] in order_link, \
            "Order link should contain the order_id"
        assert order_link == f"/orders/{order_detail['order_id']}", \
            f"Order link should be '/orders/{{order_id}}', got: {order_link}"
    
    def test_order_detail_self_link_is_accessible(self):
        """Test that OrderDetail self link is accessible"""
        # Create an order first
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        prod_id = str(uuid4())
        
        # Create an order detail
        order_detail_data = {
            "order_id": order["order_id"],
            "prod_id": prod_id,
            "quantity": 2,
            "subtotal": 199.98
        }
        response = client.post("/order-details", json=order_detail_data)
        assert response.status_code == 201
        
        order_detail = response.json()
        self_link = order_detail["links"]["self"]
        
        # Follow the self link
        get_response = client.get(self_link)
        assert get_response.status_code == 200, \
            f"Self link should be accessible, got status {get_response.status_code}"
        
        retrieved_order_detail = get_response.json()
        assert retrieved_order_detail["order_id"] == order_detail["order_id"], \
            "Self link should return the same order_detail"
        assert retrieved_order_detail["prod_id"] == order_detail["prod_id"], \
            "Self link should return the same order_detail"


class TestLinkedDataComprehensive:
    """Comprehensive tests for linked data across all resources"""
    
    def test_all_resources_have_links(self):
        """Test that all resource types include links in their responses"""
        # Create resources
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        payment = client.post("/payments", json={
            "order_id": order["order_id"],
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }).json()
        
        order_detail = client.post("/order-details", json={
            "order_id": order["order_id"],
            "prod_id": str(uuid4()),
            "quantity": 2,
            "subtotal": 199.98
        }).json()
        
        # Verify all have links
        assert "links" in order
        assert "links" in payment
        assert "links" in order_detail
        
        # Verify all have self links
        assert "self" in order["links"]
        assert "self" in payment["links"]
        assert "self" in order_detail["links"]
    
    def test_linked_resources_are_accessible(self):
        """Test that links between related resources are correct and accessible"""
        # Create an order
        order = client.post("/orders", json={
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }).json()
        
        # Create a payment linked to the order
        payment = client.post("/payments", json={
            "order_id": order["order_id"],
            "payment_method": "credit_card",
            "payment_date": datetime.utcnow().isoformat() + "Z",
            "amount": 199.99
        }).json()
        
        # Verify payment's order link points to the correct order
        payment_order_link = payment["links"]["order"]
        order_response = client.get(payment_order_link)
        assert order_response.status_code == 200
        retrieved_order = order_response.json()
        assert retrieved_order["order_id"] == order["order_id"]
        
        # Verify order's payments link includes this payment
        order_payments_link = order["links"]["payments"]
        payments_response = client.get(order_payments_link)
        assert payments_response.status_code == 200
        payments = payments_response.json()
        payment_ids = [p["payment_id"] for p in payments]
        assert payment["payment_id"] in payment_ids, \
            "Order's payments link should include the payment"
