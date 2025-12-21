"""
Test file to verify correct processing of eTag.

This test suite ensures that:
1. ETag headers are returned in responses
2. If-None-Match header works correctly for conditional GET (304 Not Modified)
3. If-Match header works correctly for conditional PUT (412 Precondition Failed, 428 Precondition Required)
4. ETag values change when resources are updated
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app

client = TestClient(app)


class TestETagProcessing:
    """Test class to verify eTag processing for GET and PUT methods"""
    
    def test_get_order_returns_etag_header(self):
        """Test that GET /orders/{order_id} returns ETag header"""
        # First create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Get the order
        response = client.get(f"/orders/{order_id}")
        
        assert response.status_code == 200, \
            f"Expected 200 OK, but got {response.status_code}. Response: {response.text}"
        
        # Verify ETag header is present
        assert "ETag" in response.headers, \
            "ETag header should be present in GET response"
        
        etag = response.headers["ETag"]
        assert etag is not None
        assert etag != "", "ETag should not be empty"
        assert etag.startswith('W/"'), "ETag should be in weak format W/\"...\""
    
    def test_get_order_with_if_none_match_matching_returns_304(self):
        """Test that GET /orders/{order_id} with matching If-None-Match returns 304 Not Modified"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Get the order to retrieve its ETag
        first_get = client.get(f"/orders/{order_id}")
        assert first_get.status_code == 200
        etag = first_get.headers["ETag"]
        
        # Get the order again with If-None-Match header matching the ETag
        response = client.get(
            f"/orders/{order_id}",
            headers={"If-None-Match": etag}
        )
        
        assert response.status_code == 304, \
            f"Expected 304 Not Modified when If-None-Match matches, but got {response.status_code}. Response: {response.text}"
        
        # Verify ETag header is still present in 304 response
        assert "ETag" in response.headers, \
            "ETag header should be present in 304 Not Modified response"
        
        # Verify response body is empty for 304
        assert not response.text or len(response.text) == 0, \
            "304 Not Modified response should have empty body"
    
    def test_get_order_with_if_none_match_non_matching_returns_200(self):
        """Test that GET /orders/{order_id} with non-matching If-None-Match returns 200 with full response"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Get the order with a non-matching If-None-Match header
        response = client.get(
            f"/orders/{order_id}",
            headers={"If-None-Match": 'W/"nonmatchingetag123"'}
        )
        
        assert response.status_code == 200, \
            f"Expected 200 OK when If-None-Match doesn't match, but got {response.status_code}. Response: {response.text}"
        
        # Verify response body contains order data
        assert response.json() is not None
        assert response.json()["order_id"] == order_id
        
        # Verify ETag header is present
        assert "ETag" in response.headers, \
            "ETag header should be present in response"
    
    def test_put_order_without_if_match_returns_428(self):
        """Test that PUT /orders/{order_id} without If-Match header returns 428 Precondition Required"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Try to update without If-Match header
        update_data = {
            "status": "shipped"
        }
        response = client.put(
            f"/orders/{order_id}",
            json=update_data
        )
        
        assert response.status_code == 428, \
            f"Expected 428 Precondition Required when If-Match is missing, but got {response.status_code}. Response: {response.text}"
        
        assert "If-Match header required" in response.json()["detail"], \
            "Error message should indicate If-Match header is required"
    
    def test_put_order_with_non_matching_if_match_returns_412(self):
        """Test that PUT /orders/{order_id} with non-matching If-Match returns 412 Precondition Failed"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Try to update with non-matching If-Match header
        update_data = {
            "status": "shipped"
        }
        response = client.put(
            f"/orders/{order_id}",
            json=update_data,
            headers={"If-Match": 'W/"nonmatchingetag123"'}
        )
        
        assert response.status_code == 412, \
            f"Expected 412 Precondition Failed when If-Match doesn't match, but got {response.status_code}. Response: {response.text}"
        
        assert "Precondition Failed" in response.json()["detail"], \
            "Error message should indicate precondition failed"
        
        # Verify current ETag is returned in headers
        assert "ETag" in response.headers, \
            "Current ETag should be returned in 412 response headers"
    
    def test_put_order_with_matching_if_match_succeeds(self):
        """Test that PUT /orders/{order_id} with matching If-Match succeeds and returns new ETag"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Get the order to retrieve its ETag
        get_response = client.get(f"/orders/{order_id}")
        assert get_response.status_code == 200
        current_etag = get_response.headers["ETag"]
        
        # Update with matching If-Match header
        update_data = {
            "status": "shipped"
        }
        response = client.put(
            f"/orders/{order_id}",
            json=update_data,
            headers={"If-Match": current_etag}
        )
        
        assert response.status_code == 200, \
            f"Expected 200 OK when If-Match matches, but got {response.status_code}. Response: {response.text}"
        
        # Verify response body contains updated order
        assert response.json() is not None
        assert response.json()["order_id"] == order_id
        assert response.json()["status"] == "shipped", \
            "Order status should be updated to 'shipped'"
        
        # Verify new ETag is returned
        assert "ETag" in response.headers, \
            "New ETag should be returned in response headers"
        
        new_etag = response.headers["ETag"]
        assert new_etag != current_etag, \
            "ETag should change after resource update"
    
    def test_etag_changes_after_update(self):
        """Test that ETag value changes when resource is updated"""
        # Create an order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # Get initial ETag
        initial_get = client.get(f"/orders/{order_id}")
        initial_etag = initial_get.headers["ETag"]
        
        # Update the order
        update_data = {
            "status": "delivered",
            "total_price": 249.99
        }
        update_response = client.put(
            f"/orders/{order_id}",
            json=update_data,
            headers={"If-Match": initial_etag}
        )
        assert update_response.status_code == 200
        
        # Get updated ETag
        updated_get = client.get(f"/orders/{order_id}")
        updated_etag = updated_get.headers["ETag"]
        
        # Verify ETag changed
        assert initial_etag != updated_etag, \
            "ETag should change when resource is updated"
        
        # Verify If-None-Match with old ETag returns 200 (not 304)
        response_with_old_etag = client.get(
            f"/orders/{order_id}",
            headers={"If-None-Match": initial_etag}
        )
        assert response_with_old_etag.status_code == 200, \
            "If-None-Match with old ETag should return 200, not 304"
        
        # Verify If-None-Match with new ETag returns 304
        response_with_new_etag = client.get(
            f"/orders/{order_id}",
            headers={"If-None-Match": updated_etag}
        )
        assert response_with_new_etag.status_code == 304, \
            "If-None-Match with current ETag should return 304 Not Modified"
    
    def test_complete_etag_workflow(self):
        """Comprehensive test of complete eTag workflow"""
        # 1. Create order
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 100.00,
            "status": "pending"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]
        
        # 2. GET order and retrieve ETag
        get1 = client.get(f"/orders/{order_id}")
        assert get1.status_code == 200
        etag1 = get1.headers["ETag"]
        assert etag1 is not None
        
        # 3. GET with If-None-Match (matching) should return 304
        get2 = client.get(f"/orders/{order_id}", headers={"If-None-Match": etag1})
        assert get2.status_code == 304
        
        # 4. PUT without If-Match should return 428
        put1 = client.put(f"/orders/{order_id}", json={"status": "shipped"})
        assert put1.status_code == 428
        
        # 5. PUT with wrong If-Match should return 412
        put2 = client.put(
            f"/orders/{order_id}",
            json={"status": "shipped"},
            headers={"If-Match": 'W/"wrongetag"'}
        )
        assert put2.status_code == 412
        
        # 6. PUT with correct If-Match should succeed
        put3 = client.put(
            f"/orders/{order_id}",
            json={"status": "shipped"},
            headers={"If-Match": etag1}
        )
        assert put3.status_code == 200
        etag2 = put3.headers["ETag"]
        assert etag2 != etag1  # ETag should change
        
        # 7. GET with old ETag in If-None-Match should return 200
        get3 = client.get(f"/orders/{order_id}", headers={"If-None-Match": etag1})
        assert get3.status_code == 200
        
        # 8. GET with new ETag in If-None-Match should return 304
        get4 = client.get(f"/orders/{order_id}", headers={"If-None-Match": etag2})
        assert get4.status_code == 304

