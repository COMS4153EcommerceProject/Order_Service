from __future__ import annotations

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr

from models.order import OrderBase


class UserBase(BaseModel):
    first_name: str = Field(
        ...,
        description="Given name.",
        json_schema_extra={"example": "Veronica"},
    )
    last_name: str = Field(
        ...,
        description="Family name.",
        json_schema_extra={"example": "Chen"},
    )
    email: EmailStr = Field(
        ...,
        description="Primary email address.",
        json_schema_extra={"example": "ada@example.com"},
    )
    dob: Optional[date] = Field(
        None,
        description="Date of birth (YYYY-MM-DD).",
        json_schema_extra={"example": "1815-12-10"},
    )

    orders: Optional[List[OrderBase]] = Field(
        None,
        description="Replace the entire set of orders with this list.",
        json_schema_extra={
            "example": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "item": "Lepro LED Desk Lamp",
                    "quantity": 1,
                    "price": 21.76,
                    "status": "shipped",
                }
            ]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "Veronica",
                    "last_name": "Chen",
                    "email": "vc@example.com",
                    "dob": "2002-09-09",
                    "orders": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "item": "Lepro LED Desk Lamp",
                            "quantity": 1,
                            "price": 21.76,
                            "status": "shipped",
                        }
                    ],
                }
            ]
        }
    }


class UserCreate(UserBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "Veronica",
                    "last_name": "Chen",
                    "email": "vc@example.com",
                    "dob": "2002-09-09",
                    "orders": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "item": "Lepro LED Desk Lamp",
                            "quantity": 1,
                            "price": 21.76,
                            "status": "shipped",
                        }
                    ],
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, json_schema_extra={"example": "Augusta"})
    last_name: Optional[str] = Field(None, json_schema_extra={"example": "King"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "ada@newmail.com"})
    dob: Optional[date] = Field(None, json_schema_extra={"example": "1815-12-10"})
    orders: Optional[List[OrderBase]] = Field(
        None,
        description="Replace the entire set of orders with this list.",
        json_schema_extra={
            "example": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "item": "Lepro LED Desk Lamp",
                    "quantity": 1,
                    "price": 21.76,
                    "status": "shipped",
                }
            ]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"first_name": "Ada", "last_name": "Byron"},
                {"email": "ada@newmail.com"},
                {
                    "orders": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "item": "Lepro LED Desk Lamp",
                            "quantity": 1,
                            "price": 21.76,
                            "status": "shipped",
                        }
                    ],
                }
            ]
        }
    }


class UserRead(UserBase):
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Person ID.",
        json_schema_extra={"example": "99999999-9999-4999-8999-999999999999"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "first_name": "Veronica",
                    "last_name": "Chen",
                    "email": "vc@example.com",
                    "dob": "2002-09-09",
                    "orders": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "item": "Lepro LED Desk Lamp",
                            "quantity": 1,
                            "price": 21.76,
                            "status": "shipped",
                        }
                    ],
                }
            ]
        }
    }
