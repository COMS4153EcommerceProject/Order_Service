from __future__ import annotations
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException, Query

from models.payment import PaymentCreate, PaymentRead, PaymentUpdate

# In-memory storage for payments
payments: Dict[UUID, PaymentRead] = {}

class PaymentResource:
    """Resource class for Payment CRUD operations"""
    
    @staticmethod
    def create_payment(payment: PaymentCreate) -> PaymentRead:
        """Create a new payment"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
    
    @staticmethod
    def get_payments(
        order_id: Optional[UUID] = Query(None),
        payment_method: Optional[str] = Query(None),
    ) -> List[PaymentRead]:
        """Get all payments with optional filtering"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
    
    @staticmethod
    def get_payment(payment_id: UUID) -> PaymentRead:
        """Get a specific payment by ID"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
    
    @staticmethod
    def update_payment(payment_id: UUID, update: PaymentUpdate) -> PaymentRead:
        """Update an existing payment"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
    
    @staticmethod
    def delete_payment(payment_id: UUID) -> PaymentRead:
        """Delete a payment"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
