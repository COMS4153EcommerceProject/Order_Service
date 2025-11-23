from __future__ import annotations
import threading
import time
from typing import Dict, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from models.order import OrderCreate, OrderRead
from resources.order_resource import OrderResource


# In-memory storage for task statuses (simple dict structure)
task_statuses: Dict[UUID, Dict[str, Any]] = {}


def process_order_async(task_id: UUID, order_data: OrderCreate):
    """
    Background task to process an order asynchronously.
    Simulates order processing steps: validation, inventory check, payment processing, etc.
    """
    try:
        # Update status to processing
        if task_id in task_statuses:
            task_statuses[task_id]["status"] = "processing"
            task_statuses[task_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Simulate processing steps with delays
        time.sleep(2)  # Simulate validation
        
        time.sleep(2)  # Simulate inventory check
        
        time.sleep(2)  # Simulate payment processing
        
        # Create the order
        order = OrderResource.create_order(order_data)
        
        # Update task status to completed
        if task_id in task_statuses:
            task_statuses[task_id]["status"] = "completed"
            task_statuses[task_id]["updated_at"] = datetime.utcnow().isoformat()
            task_statuses[task_id]["result"] = {
                "order_id": str(order.order_id),
                "order": order.model_dump(mode='json')
            }
    except Exception as e:
        # Update task status to failed
        if task_id in task_statuses:
            task_statuses[task_id]["status"] = "failed"
            task_statuses[task_id]["updated_at"] = datetime.utcnow().isoformat()
            task_statuses[task_id]["error"] = str(e)


class OrderProcessingService:
    """Service for managing asynchronous order processing"""
    
    @staticmethod
    def start_order_processing(order_data: OrderCreate) -> Dict[str, Any]:
        """
        Start asynchronous order processing and return task info.
        
        Args:
            order_data: The order data to process
            
        Returns:
            Dict with task_id and status URL
        """
        # Generate task ID
        task_id = uuid4()
        now = datetime.utcnow().isoformat()
        
        # Create initial task status (simple dict)
        task_status = {
            "task_id": str(task_id),
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "result": None,
            "error": None
        }
        
        # Store task status
        task_statuses[task_id] = task_status
        
        # Start background thread to process the order
        thread = threading.Thread(
            target=process_order_async,
            args=(task_id, order_data),
            daemon=True
        )
        thread.start()
        
        return {
            "task_id": str(task_id),
            "status_url": f"/tasks/{task_id}/status"
        }
    
    @staticmethod
    def get_task_status(task_id: UUID) -> Dict[str, Any]:
        """
        Get the status of an async task.
        
        Args:
            task_id: The task ID to check
            
        Returns:
            Dict with current task status
            
        Raises:
            HTTPException: If task not found
        """
        from fastapi import HTTPException
        
        if task_id not in task_statuses:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = task_statuses[task_id].copy()
        task["links"] = {
            "self": f"/tasks/{task_id}",
            "status": f"/tasks/{task_id}/status"
        }
        
        return task

