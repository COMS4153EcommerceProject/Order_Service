from __future__ import annotations
from typing import Dict, Any
from uuid import UUID


def generate_order_links(order_id: UUID) -> Dict[str, str]:
    """
    Generate relative path links for an order resource.
    
    Args:
        order_id: The order UUID
    
    Returns:
        Dictionary with relative path links
    """
    return {
        "self": f"/orders/{order_id}",
        "payments": f"/payments?order_id={order_id}",
        "order_details": f"/order-details?order_id={order_id}"
    }


def generate_payment_links(payment_id: UUID, order_id: UUID) -> Dict[str, str]:
    """
    Generate relative path links for a payment resource.
    
    Args:
        payment_id: The payment UUID
        order_id: The associated order UUID
    
    Returns:
        Dictionary with relative path links
    """
    return {
        "self": f"/payments/{payment_id}",
        "order": f"/orders/{order_id}"
    }


def generate_order_detail_links(order_id: UUID, prod_id: UUID) -> Dict[str, str]:
    """
    Generate relative path links for an order detail resource.
    
    Args:
        order_id: The order UUID
        prod_id: The product UUID
    
    Returns:
        Dictionary with relative path links
    """
    return {
        "self": f"/order-details/{order_id}/{prod_id}",
        "order": f"/orders/{order_id}"
    }

