from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserIn(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "staff"


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    status: str
    created_at: Optional[datetime] = None


class CustomerIn(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    address: Optional[str]
    created_at: Optional[datetime] = None


class BranchIn(BaseModel):
    name: str
    city: str
    address: Optional[str] = None
    phone: Optional[str] = None


class BranchOut(BaseModel):
    id: int
    name: str
    city: str
    address: Optional[str]
    phone: Optional[str]
    created_at: Optional[datetime] = None


class CourierIn(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    vehicle_no: Optional[str] = None
    branch_id: Optional[int] = None


class CourierOut(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    vehicle_no: Optional[str]
    branch_id: Optional[int]
    branch_name: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None


class ParcelIn(BaseModel):
    sender_id: int
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    pickup_branch_id: Optional[int] = None
    delivery_branch_id: Optional[int] = None
    courier_id: Optional[int] = None
    parcel_type: str = "box"
    weight_kg: float = 1.0
    cost: float = 0.0
    payment_status: str = "unpaid"
    booking_date: str
    expected_delivery_date: Optional[str] = None


class ParcelOut(BaseModel):
    id: int
    tracking_no: str
    sender_id: int
    sender_name: Optional[str] = None
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    pickup_branch_id: Optional[int]
    pickup_branch_name: Optional[str] = None
    delivery_branch_id: Optional[int]
    delivery_branch_name: Optional[str] = None
    courier_id: Optional[int]
    courier_name: Optional[str] = None
    parcel_type: str
    weight_kg: float
    cost: float
    payment_status: str
    status: str
    booking_date: str
    expected_delivery_date: Optional[str]
    delivered_at: Optional[datetime]
    created_by: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StatusUpdateIn(BaseModel):
    status: str
    location: Optional[str] = None
    remarks: Optional[str] = None


class TrackingEntryOut(BaseModel):
    id: int
    parcel_id: int
    status: str
    location: Optional[str]
    remarks: Optional[str]
    updated_by: Optional[int]
    updated_by_name: Optional[str] = None
    updated_at: Optional[datetime] = None


class DashboardStats(BaseModel):
    total_parcels: int
    pending: int
    in_transit: int
    out_for_delivery: int
    delivered: int
    customers: int
    couriers: int
    revenue: float
