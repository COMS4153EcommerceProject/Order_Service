from __future__ import annotations
import os
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query

from models.order import OrderCreate, OrderRead, OrderUpdate
from models.payment import PaymentCreate, PaymentRead, PaymentUpdate
from models.order_detail import OrderDetailCreate, OrderDetailRead, OrderDetailUpdate

from resources.order_resource import OrderResource
from resources.payment_resource import PaymentResource
from resources.order_detail_resource import OrderDetailResource

port = int(os.environ.get("FASTAPIPORT", 8000))

app = FastAPI(
    title="Order Management API",
    description="Microservice for managing user orders, payments, and order details",
    version="0.1.0",
)

# --------------------------------------------------------------------------
# Order endpoints
# --------------------------------------------------------------------------
@app.post("/orders", response_model=OrderRead, status_code=201)
def create_order(order: OrderCreate):
    """Create a new order"""
    return OrderResource.create_order(order)

@app.get("/orders", response_model=List[OrderRead])
def list_orders(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by order status"),
):
    """Get all orders with optional filtering"""
    return OrderResource.get_orders(user_id=user_id, status=status)

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: UUID):
    """Get a specific order by ID"""
    return OrderResource.get_order(order_id)

@app.put("/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: UUID, update: OrderUpdate):
    """Update an existing order"""
    return OrderResource.update_order(order_id, update)

@app.delete("/orders/{order_id}", response_model=OrderRead)
def delete_order(order_id: UUID):
    """Delete an order"""
    return OrderResource.delete_order(order_id)

# --------------------------------------------------------------------------
# Payment endpoints
# --------------------------------------------------------------------------
@app.post("/payments", response_model=PaymentRead, status_code=201)
def create_payment(payment: PaymentCreate):
    """Create a new payment"""
    return PaymentResource.create_payment(payment)

@app.get("/payments", response_model=List[PaymentRead])
def list_payments(
    order_id: Optional[UUID] = Query(None, description="Filter by order ID"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
):
    """Get all payments with optional filtering"""
    return PaymentResource.get_payments(order_id=order_id, payment_method=payment_method)

@app.get("/payments/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: UUID):
    """Get a specific payment by ID"""
    return PaymentResource.get_payment(payment_id)

@app.put("/payments/{payment_id}", response_model=PaymentRead)
def update_payment(payment_id: UUID, update: PaymentUpdate):
    """Update an existing payment"""
    return PaymentResource.update_payment(payment_id, update)

@app.delete("/payments/{payment_id}", response_model=PaymentRead)
def delete_payment(payment_id: UUID):
    """Delete a payment"""
    return PaymentResource.delete_payment(payment_id)

# --------------------------------------------------------------------------
# Order Detail endpoints
# --------------------------------------------------------------------------
@app.post("/order-details", response_model=OrderDetailRead, status_code=201)
def create_order_detail(order_detail: OrderDetailCreate):
    """Create a new order detail"""
    return OrderDetailResource.create_order_detail(order_detail)

@app.get("/order-details", response_model=List[OrderDetailRead])
def list_order_details(
    order_id: Optional[UUID] = Query(None, description="Filter by order ID"),
    prod_id: Optional[UUID] = Query(None, description="Filter by product ID"),
):
    """Get all order details with optional filtering"""
    return OrderDetailResource.get_order_details(order_id=order_id, prod_id=prod_id)

@app.get("/order-details/{order_id}/{prod_id}", response_model=OrderDetailRead)
def get_order_detail(order_id: UUID, prod_id: UUID):
    """Get a specific order detail by composite key (order_id, prod_id)"""
    return OrderDetailResource.get_order_detail(order_id, prod_id)

@app.put("/order-details/{order_id}/{prod_id}", response_model=OrderDetailRead)
def update_order_detail(order_id: UUID, prod_id: UUID, update: OrderDetailUpdate):
    """Update an existing order detail"""
    return OrderDetailResource.update_order_detail(order_id, prod_id, update)

@app.delete("/order-details/{order_id}/{prod_id}", response_model=OrderDetailRead)
def delete_order_detail(order_id: UUID, prod_id: UUID):
    """Delete an order detail"""
    return OrderDetailResource.delete_order_detail(order_id, prod_id)

# --------------------------------------------------------------------------
# Root
# --------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Welcome to the Order Management API. See /docs for OpenAPI UI.",
        "version": "0.1.0",
        "entities": ["orders", "payments", "order-details"]
    }

# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)