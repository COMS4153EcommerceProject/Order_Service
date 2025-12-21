"""
Test file to verify correct implementation of 202 Accepted with asynchronous 
implementation and polling for status.

This test suite ensures that:
1. POST /orders/process returns 202 Accepted status code
2. Response includes task_id and status_url for polling
3. Status polling endpoint works correctly
4. Task status transitions: pending -> completed/failed
5. Polling can track the progress of async operations
"""
import pytest
import time
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app

client = TestClient(app)


class Test202AcceptedAsyncProcessing:
    """Test 202 Accepted status code for asynchronous order processing"""
    
    def test_post_orders_process_returns_202(self):
        """Test that POST /orders/process returns 202 Accepted"""
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        
        response = client.post("/orders/process", json=order_data)
        
        assert response.status_code == 202, \
            f"Expected 202 Accepted, but got {response.status_code}. Response: {response.text}"


class TestTaskStatusPolling:
    """Test polling for task status"""
    
    def test_get_task_status_initial_status(self):
        """Test that newly created task has valid initial status"""
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        
        # Start async processing
        process_response = client.post("/orders/process", json=order_data)
        assert process_response.status_code == 202
        
        task_id = process_response.json()["task_id"]
        status_url = process_response.json()["status_url"]
        
        # Poll status immediately (could be pending or processing depending on timing)
        status_response = client.get(status_url)
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        # Initial status could be "pending" or "processing" due to async execution
        assert status_data["status"] in ["pending", "processing"], \
            f"Task should be 'pending' or 'processing' initially, got: {status_data['status']}"
        assert status_data["task_id"] == task_id, \
            "Status response should contain correct task_id"


class TestAsyncTaskLifecycle:
    """Test the complete lifecycle of async task processing"""
    
    def test_task_status_transitions_pending_to_processing_to_completed(self):
        """Test that task status transitions correctly through lifecycle"""
        order_data = {
            "user_id": str(uuid4()),
            "total_price": 199.99,
            "status": "pending"
        }
        
        # Start async processing
        process_response = client.post("/orders/process", json=order_data)
        assert process_response.status_code == 202
        
        task_id = process_response.json()["task_id"]
        status_url = process_response.json()["status_url"]
        
        # Initial status could be pending or processing
        status_response = client.get(status_url)
        status_data = status_response.json()
        initial_status = status_data["status"]
        assert initial_status in ["pending", "processing"], \
            f"Initial status should be 'pending' or 'processing', got: {initial_status}"
        
        max_wait = 10
        elapsed = 0
        while elapsed < max_wait:
            status_response = client.get(status_url)
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Task failed with error: {status_data.get('error', 'Unknown error')}")
            
            time.sleep(0.5)
            elapsed += 0.5
        
        # Final status should be completed
        assert status_data["status"] == "completed", \
            f"Task should be 'completed' after processing, got: {status_data['status']}"
    