from pydantic import BaseModel
from datetime import date
from typing import Optional
from fastapi import UploadFile, File


# Schema for FuelPurchase responses
class FuelPurchaseBase(BaseModel):
    vehicle_id: int
    driver_id: int
    quantity: int
    unit_cost: float
    total_cost: float
    purchase_date: Optional[date] = None
    tenancy_id: int


# Schema for requests to create a FuelPurchase
class FuelPurchaseCreate(FuelPurchaseBase):
    file_path: str


# Schema for requests to update a FuelPurchase
class FuelPurchaseUpdate(BaseModel):
    vehicle_id: int
    quantity: int
    unit_cost: float
    total_cost: float
    purchase_date: date


# Schema for reading a FuelPurchase
class FuelPurchaseRead(FuelPurchaseBase):
    id: int

    class Config:
        from_attributes = True
