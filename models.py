from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    staff = "staff"
    cashier = "cashier"


class ParcelStatus(str, Enum):
    pending = "pending"
    picked_up = "picked_up"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"


class PaymentStatus(str, Enum):
    unpaid = "unpaid"
    paid = "paid"


class CourierStatus(str, Enum):
    available = "available"
    busy = "busy"
    off_duty = "off_duty"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class ParcelType(str, Enum):
    document = "document"
    box = "box"
    fragile = "fragile"
    electronics = "electronics"
    other = "other"
