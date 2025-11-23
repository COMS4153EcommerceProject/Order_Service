from __future__ import annotations
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException

from models.order import OrderCreate, OrderRead, OrderUpdate
from utils.links import generate_order_links

# In-memory storage for orders
orders: Dict[UUID, OrderRead] = {}

class OrderResource:
    """Resource class for Order CRUD operations"""
    
    @staticmethod
    def create_order(order: OrderCreate) -> OrderRead:
        """Create a new order"""
        # Generate a new order_id
        order_id = uuid4()
        
        # Get current timestamp
        now = datetime.utcnow()
        
        # Create OrderRead from OrderCreate with generated fields
        new_order = OrderRead(
            order_id=order_id,
            user_id=order.user_id,
            order_date=now,
            total_price=order.total_price,
            status=order.status,
            created_at=now,
            updated_at=now,
            links=generate_order_links(order_id)
        )
        
        # Store in memory
        orders[order_id] = new_order
        
        return new_order
    
    @staticmethod
    def get_orders(
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        order_date_from: Optional[datetime] = None,
        order_date_to: Optional[datetime] = None,
        min_total_price: Optional[float] = None,
        max_total_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[OrderRead]:
        """Get all orders with optional filtering, sorting, and pagination"""
        # Get all orders as a list
        all_orders = list(orders.values())
        
        # Apply filters if provided
        filtered_orders = all_orders
        
        if user_id is not None:
            filtered_orders = [order for order in filtered_orders if order.user_id == user_id]
        
        if status is not None:
            filtered_orders = [order for order in filtered_orders if order.status == status]
        
        if order_date_from is not None:
            filtered_orders = [order for order in filtered_orders if order.order_date >= order_date_from]
        
        if order_date_to is not None:
            filtered_orders = [order for order in filtered_orders if order.order_date <= order_date_to]
        
        if min_total_price is not None:
            filtered_orders = [order for order in filtered_orders if order.total_price >= min_total_price]
        
        if max_total_price is not None:
            filtered_orders = [order for order in filtered_orders if order.total_price <= max_total_price]
        
        # Apply sorting
        if sort_by is not None:
            sort_fields = {
                "order_id": lambda o: o.order_id,
                "user_id": lambda o: o.user_id,
                "order_date": lambda o: o.order_date,
                "total_price": lambda o: o.total_price,
                "status": lambda o: o.status,
                "created_at": lambda o: o.created_at,
                "updated_at": lambda o: o.updated_at,
            }
            
            if sort_by in sort_fields:
                reverse = order and order.lower() == "desc"
                filtered_orders = sorted(filtered_orders, key=sort_fields[sort_by], reverse=reverse)
        
        # Apply pagination
        if offset is not None and offset > 0:
            filtered_orders = filtered_orders[offset:]
        
        if limit is not None and limit > 0:
            filtered_orders = filtered_orders[:limit]
        
        # Ensure links are populated for all orders
        for order in filtered_orders:
            if not order.links or len(order.links) == 0:
                order.links = generate_order_links(order.order_id)
        
        return filtered_orders
    
    @staticmethod
    def get_order(order_id: UUID) -> OrderRead:
        """Get a specific order by ID"""
        if order_id not in orders:
            raise HTTPException(status_code=404, detail="Order not found")
        order = orders[order_id]
        # Ensure links are populated
        if not order.links or len(order.links) == 0:
            order.links = generate_order_links(order_id)
        return order
    
    @staticmethod
    def update_order(order_id: UUID, update: OrderUpdate) -> OrderRead:
        """Update an existing order"""
        if order_id not in orders:
            raise HTTPException(status_code=404, detail="Order not found")
        
        existing_order = orders[order_id]
        
        # Update fields that are provided
        update_data = update.model_dump(exclude_unset=True)
        updated_order_data = existing_order.model_dump()
        updated_order_data.update(update_data)
        updated_order_data['updated_at'] = datetime.utcnow()
        
        # Create updated order
        updated_order = OrderRead(**updated_order_data)
        # Ensure links are populated
        updated_order.links = generate_order_links(order_id)
        orders[order_id] = updated_order
        
        return updated_order
    
    @staticmethod
    def delete_order(order_id: UUID) -> OrderRead:
        """Delete an order"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
