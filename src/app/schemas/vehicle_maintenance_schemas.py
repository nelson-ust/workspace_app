from pydantic import BaseModel
from datetime import date
from typing import Text

# Schema for VehicleMaintenance responses
class VehicleMaintenanceBase(BaseModel):
    vehicle_id: int
    maintenance_type_id:int
    description:Text
    cost:float
    maintenance_date:date
    tenancy_id:int

# Schema for requests to create a VehicleMaintenance
class VehicleMaintenanceCreate(VehicleMaintenanceBase):
    pass

# Schema for requests to update a VehicleMaintenance
class VehicleMaintenanceUpdate(BaseModel):
    vehicle_id: int
    maintenance_type_id:int
    description:Text
    cost:float
    maintenance_date:date
    tenancy_id:int

# Schema for reading a VehicleMaintenance
class VehicleMaintenanceRead(VehicleMaintenanceBase):
    pass

    class Config:
        from_attributes = True
