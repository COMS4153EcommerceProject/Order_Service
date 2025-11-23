from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

from models.order_detail import OrderDetailCreate, OrderDetailRead, OrderDetailUpdate
from utils.links import generate_order_detail_links

# In-memory storage for order details (using composite key: (order_id, prod_id))
order_details: Dict[Tuple[UUID, UUID], OrderDetailRead] = {}

class OrderDetailResource:
    """Resource class for Order_Detail CRUD operations"""
    
    @staticmethod
    def create_order_detail(order_detail: OrderDetailCreate) -> OrderDetailRead:
        """Create a new order detail"""
        # Get current timestamp
        now = datetime.utcnow()
        
        # Create OrderDetailRead from OrderDetailCreate with generated fields
        new_order_detail = OrderDetailRead(
            order_id=order_detail.order_id,
            prod_id=order_detail.prod_id,
            quantity=order_detail.quantity,
            subtotal=order_detail.subtotal,
            created_at=now,
            updated_at=now,
            links=generate_order_detail_links(order_detail.order_id, order_detail.prod_id)
        )
        
        # Store in memory
        key = (order_detail.order_id, order_detail.prod_id)
        order_details[key] = new_order_detail
        
        return new_order_detail
    
    @staticmethod
    def get_order_details(
        order_id: Optional[UUID] = None,
        prod_id: Optional[UUID] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None,
        min_subtotal: Optional[float] = None,
        max_subtotal: Optional[float] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[OrderDetailRead]:
        """Get all order details with optional filtering, sorting, and pagination"""
        # Get all order details as a list
        all_order_details = list(order_details.values())
        
        # Apply filters if provided
        filtered_order_details = all_order_details
        
        if order_id is not None:
            filtered_order_details = [detail for detail in filtered_order_details if detail.order_id == order_id]
        
        if prod_id is not None:
            filtered_order_details = [detail for detail in filtered_order_details if detail.prod_id == prod_id]
        
        if min_quantity is not None:
            filtered_order_details = [detail for detail in filtered_order_details if detail.quantity >= min_quantity]
        
        if max_quantity is not None:
            filtered_order_details = [detail for detail in filtered_order_details if detail.quantity <= max_quantity]
        
        if min_subtotal is not None:
            filtered_order_details = [detail for detail in filtered_order_details if detail.subtotal >= min_subtotal]
        
        if max_subtotal is not None:
            filtered_order_details = [detail for detail in filtered_order_details if detail.subtotal <= max_subtotal]
        
        # Apply sorting
        if sort_by is not None:
            sort_fields = {
                "order_id": lambda d: d.order_id,
                "prod_id": lambda d: d.prod_id,
                "quantity": lambda d: d.quantity,
                "subtotal": lambda d: d.subtotal,
                "created_at": lambda d: d.created_at,
                "updated_at": lambda d: d.updated_at,
            }
            
            if sort_by in sort_fields:
                reverse = order and order.lower() == "desc"
                filtered_order_details = sorted(filtered_order_details, key=sort_fields[sort_by], reverse=reverse)
        
        # Apply pagination
        if offset is not None and offset > 0:
            filtered_order_details = filtered_order_details[offset:]
        
        if limit is not None and limit > 0:
            filtered_order_details = filtered_order_details[:limit]
        
        # Ensure links are populated for all order details
        for detail in filtered_order_details:
            if not detail.links or len(detail.links) == 0:
                detail.links = generate_order_detail_links(detail.order_id, detail.prod_id)
        
        return filtered_order_details
    
    @staticmethod
    def get_order_detail(order_id: UUID, prod_id: UUID) -> OrderDetailRead:
        """Get a specific order detail by composite key (order_id, prod_id)"""
        key = (order_id, prod_id)
        if key not in order_details:
            raise HTTPException(status_code=404, detail="Order detail not found")
        detail = order_details[key]
        # Ensure links are populated
        if not detail.links or len(detail.links) == 0:
            detail.links = generate_order_detail_links(order_id, prod_id)
        return detail
    
    @staticmethod
    def update_order_detail(order_id: UUID, prod_id: UUID, update: OrderDetailUpdate) -> OrderDetailRead:
        """Update an existing order detail"""
        key = (order_id, prod_id)
        if key not in order_details:
            raise HTTPException(status_code=404, detail="Order detail not found")
        
        existing_detail = order_details[key]
        
        # Update fields that are provided
        update_data = update.model_dump(exclude_unset=True)
        updated_detail_data = existing_detail.model_dump()
        updated_detail_data.update(update_data)
        updated_detail_data['updated_at'] = datetime.utcnow()
        
        # Create updated order detail
        updated_detail = OrderDetailRead(**updated_detail_data)
        # Ensure links are populated
        updated_detail.links = generate_order_detail_links(order_id, prod_id)
        order_details[key] = updated_detail
        
        return updated_detail
    
    @staticmethod
    def delete_order_detail(order_id: UUID, prod_id: UUID) -> OrderDetailRead:
        """Delete an order detail"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
