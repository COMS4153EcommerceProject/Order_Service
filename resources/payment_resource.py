from __future__ import annotations
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException

from models.payment import PaymentCreate, PaymentRead, PaymentUpdate
from utils.links import generate_payment_links

# In-memory storage for payments
payments: Dict[UUID, PaymentRead] = {}

class PaymentResource:
    """Resource class for Payment CRUD operations"""
    
    @staticmethod
    def create_payment(payment: PaymentCreate) -> PaymentRead:
        """Create a new payment"""
        # Generate a new payment_id
        payment_id = uuid4()
        
        # Get current timestamp
        now = datetime.utcnow()
        
        # Create PaymentRead from PaymentCreate with generated fields
        new_payment = PaymentRead(
            payment_id=payment_id,
            order_id=payment.order_id,
            payment_method=payment.payment_method,
            payment_date=payment.payment_date,
            amount=payment.amount,
            created_at=now,
            updated_at=now,
            links=generate_payment_links(payment_id, payment.order_id)
        )
        
        # Store in memory
        payments[payment_id] = new_payment
        
        return new_payment
    
    @staticmethod
    def get_payments(
        order_id: Optional[UUID] = None,
        payment_method: Optional[str] = None,
        payment_date_from: Optional[datetime] = None,
        payment_date_to: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[PaymentRead]:
        """Get all payments with optional filtering, sorting, and pagination"""
        # Get all payments as a list
        all_payments = list(payments.values())
        
        # Apply filters if provided
        filtered_payments = all_payments
        
        if order_id is not None:
            filtered_payments = [payment for payment in filtered_payments if payment.order_id == order_id]
        
        if payment_method is not None:
            filtered_payments = [payment for payment in filtered_payments if payment.payment_method == payment_method]
        
        if payment_date_from is not None:
            filtered_payments = [payment for payment in filtered_payments if payment.payment_date >= payment_date_from]
        
        if payment_date_to is not None:
            filtered_payments = [payment for payment in filtered_payments if payment.payment_date <= payment_date_to]
        
        if min_amount is not None:
            filtered_payments = [payment for payment in filtered_payments if payment.amount >= min_amount]
        
        if max_amount is not None:
            filtered_payments = [payment for payment in filtered_payments if payment.amount <= max_amount]
        
        # Apply sorting
        if sort_by is not None:
            sort_fields = {
                "payment_id": lambda p: p.payment_id,
                "order_id": lambda p: p.order_id,
                "payment_method": lambda p: p.payment_method,
                "payment_date": lambda p: p.payment_date,
                "amount": lambda p: p.amount,
                "created_at": lambda p: p.created_at,
                "updated_at": lambda p: p.updated_at,
            }
            
            if sort_by in sort_fields:
                reverse = order and order.lower() == "desc"
                filtered_payments = sorted(filtered_payments, key=sort_fields[sort_by], reverse=reverse)
        
        # Apply pagination
        if offset is not None and offset > 0:
            filtered_payments = filtered_payments[offset:]
        
        if limit is not None and limit > 0:
            filtered_payments = filtered_payments[:limit]
        
        # Ensure links are populated for all payments
        for payment in filtered_payments:
            if not payment.links or len(payment.links) == 0:
                payment.links = generate_payment_links(payment.payment_id, payment.order_id)
        
        return filtered_payments
    
    @staticmethod
    def get_payment(payment_id: UUID) -> PaymentRead:
        """Get a specific payment by ID"""
        if payment_id not in payments:
            raise HTTPException(status_code=404, detail="Payment not found")
        payment = payments[payment_id]
        # Ensure links are populated
        if not payment.links or len(payment.links) == 0:
            payment.links = generate_payment_links(payment_id, payment.order_id)
        return payment
    
    @staticmethod
    def update_payment(payment_id: UUID, update: PaymentUpdate) -> PaymentRead:
        """Update an existing payment"""
        if payment_id not in payments:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        existing_payment = payments[payment_id]
        
        # Update fields that are provided
        update_data = update.model_dump(exclude_unset=True)
        updated_payment_data = existing_payment.model_dump()
        updated_payment_data.update(update_data)
        updated_payment_data['updated_at'] = datetime.utcnow()
        
        # Create updated payment
        updated_payment = PaymentRead(**updated_payment_data)
        # Links are populated
        updated_payment.links = generate_payment_links(payment_id, updated_payment.order_id)
        payments[payment_id] = updated_payment
        
        return updated_payment
    
    @staticmethod
    def delete_payment(payment_id: UUID) -> PaymentRead:
        """Delete a payment"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
