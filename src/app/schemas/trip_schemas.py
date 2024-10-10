
# from datetime import date, datetime
# from pydantic import BaseModel, Field, validator
# from typing import List, Optional

# class TripSummarySchema(BaseModel):
#     trip_start_time: Optional[str] = None
#     activity_date: date
#     employee_names: List[str]
#     vehicle_name: str
#     location_names: List[str]
#     site_names: List[str]
#     trip_lead: str
#     driver_name: str
#     activity_title: str
#     workplan_code: str
#     vehicle_license_plate: str

#     @validator('trip_start_time', pre=True, always=True)
#     def parse_time(cls, value):
#         if value is None:
#             return None
#         try:
#             # Ensure the use of datetime.strptime from the datetime class correctly.
#             return datetime.strptime(value, '%I:%M %p').time()
#         except ValueError:
#             raise ValueError("Time must be in 'HH:MM AM/PM' format")

#     class Config:
#         orm_mode = True



# class EndTripRequest(BaseModel):
#     mileage_end: float = Field(..., gt=0, description="The ending mileage of the vehicle at the end of the trip. Must be greater than zero."),
#     trip_end_location_id: int= Field(..., description= "The Trip end Location.")
#     # tenancy_id: int = Field(...,description="The Associated Tenancy Id for the Trip")
#     class Config:
#         schema_extra = {
#             "example": { 
#                 "mileage_end": 12345.67,
#                 # "tenancy_id":1
#             }
#         }

# class EndTripResponse(BaseModel):
#     message: str = Field(description="A message indicating the result of the operation.")
#     trip_id: int = Field(description="The ID of the trip that was ended.")
#     mileage_start: float = Field(description="The mileage of the vehicle at the start of the trip.")
#     mileage_end: float = Field(description="The mileage of the vehicle at the end of the trip.")
#     distance_travelled: float = Field(description="The calculated distance traveled during the trip.")

#     class Config:
#         schema_extra = {
#             "example": {
#                 "message": "Trip successfully ended.",
#                 "trip_id": 123,
#                 "mileage_start": 12000.5,
#                 "mileage_end": 12150.5,
#                 "distance_travelled": 150.0
#             }
        
#         }

# class AssignVehicleDriverRequest(BaseModel):
#     work_plan_ids: List[int]
#     employee_ids: List[int]  # Add this line
#     vehicle_id: int
#     driver_id: int
#     auto_group_weekly: bool

# class TripSummary(BaseModel):
#     work_plan_id: int
#     activity_title: Optional[str]
#     workplan_code: Optional[str]
#     trip_start_time: Optional[str]
#     actual_start_time: Optional[str]
#     activity_date: str
#     workplan_source_name: str
#     implementing_team: str
#     trip_status: str
#     trip_lead: Optional[str]
#     employee_names: List[str]
#     vehicle_name: Optional[str]
#     vehicle_license_plate: Optional[str]
#     driver_name: Optional[str]
#     location_names: List[str]
#     site_names: List[str]

#     class Config:
#         orm_mode = True  # Allows the model to work with ORM models (like SQLAlchemy models)

# class EmployeeRead(BaseModel):
#     id: int
#     first_name: str
#     last_name: str
#     full_name: str
#     email: str
#     phone_number: str

#     class Config:
#         orm_mode = True

# class GetEmployeesNotInTripRequest(BaseModel):
#     work_plan_ids: List[int]

# class RecordStageRequest(BaseModel):
#     trip_id: int
#     site_id: int
#     mileage: float
    
# class RecordMileageRequest(BaseModel):
#     trip_id: int
#     site_id: int
#     mileage_at_arrival: float


# class ArrivalRequest(BaseModel):
#     site_id: int
#     mileage_at_arrival: float

# class ArrivalResponse(BaseModel):
#     message: str
#     trip_stage: dict
#     vehicle_current_mileage: float

# class TripArrivalRequest(BaseModel):
#     mileage_at_arrival: float

# class TripArrivalResponse(BaseModel):
#     message: str
#     trip_stage: dict
#     vehicle_current_mileage: float

# class DepartureRequest(BaseModel):
#     next_site_id: Optional[int] = None

# class DepartureResponse(BaseModel):
#     message: str
#     trip_stage: dict
#     next_site_id: Optional[int] = None
#     next_stage_id: Optional[int] = None

# class DropEmployeesFromTripRequest(BaseModel):
#     employee_ids: List[int]





from datetime import date, datetime
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class TripSummarySchema(BaseModel):
    trip_start_time: Optional[str] = None
    activity_date: date
    employee_names: List[str]
    vehicle_name: str
    location_names: List[str]
    site_names: List[str]
    trip_lead: str
    driver_name: str
    activity_title: str
    workplan_code: str
    vehicle_license_plate: str

    @validator('trip_start_time', pre=True, always=True)
    def parse_time(cls, value):
        if value is None:
            return None
        try:
            # Ensure the use of datetime.strptime from the datetime class correctly.
            return datetime.strptime(value, '%I:%M %p').time()
        except ValueError:
            raise ValueError("Time must be in 'HH:MM AM/PM' format")

    class Config:
        orm_mode = True



class EndTripRequest(BaseModel):
    mileage_end: float = Field(..., gt=0, description="The ending mileage of the vehicle at the end of the trip. Must be greater than zero."),
    trip_end_location_id: int= Field(..., description= "The Trip end Location.")
    # tenancy_id: int = Field(...,description="The Associated Tenancy Id for the Trip")
    class Config:
        schema_extra = {
            "example": { 
                "mileage_end": 12345.67,
                # "tenancy_id":1
            }
        }

class EndTripResponse(BaseModel):
    message: str = Field(description="A message indicating the result of the operation.")
    trip_id: int = Field(description="The ID of the trip that was ended.")
    mileage_start: float = Field(description="The mileage of the vehicle at the start of the trip.")
    mileage_end: float = Field(description="The mileage of the vehicle at the end of the trip.")
    distance_travelled: float = Field(description="The calculated distance traveled during the trip.")

    class Config:
        schema_extra = {
            "example": {
                "message": "Trip successfully ended.",
                "trip_id": 123,
                "mileage_start": 12000.5,
                "mileage_end": 12150.5,
                "distance_travelled": 150.0
            }
        
        }

class AssignVehicleDriverRequest(BaseModel):
    work_plan_ids: List[int]
    employee_ids: List[int]  # Add this line
    vehicle_id: int
    driver_id: int
    auto_group_weekly: bool

class TripSummary(BaseModel):
    work_plan_id: int
    activity_title: Optional[str]
    workplan_code: Optional[str]
    trip_start_time: Optional[str]
    actual_start_time: Optional[str]
    activity_date: str
    workplan_source_name: str
    implementing_team: str
    trip_status: str
    trip_lead: Optional[str]
    employee_names: List[str]
    vehicle_name: Optional[str]
    vehicle_license_plate: Optional[str]
    driver_name: Optional[str]
    location_names: List[str]
    site_names: List[str]

    class Config:
        orm_mode = True  # Allows the model to work with ORM models (like SQLAlchemy models)

class EmployeeRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone_number: str

    class Config:
        orm_mode = True

class GetEmployeesNotInTripRequest(BaseModel):
    work_plan_ids: List[int]

class RecordStageRequest(BaseModel):
    trip_id: int
    site_id: int
    mileage: float
    
class RecordMileageRequest(BaseModel):
    trip_id: int
    site_id: int
    mileage_at_arrival: float


class ArrivalRequest(BaseModel):
    site_id: int
    mileage_at_arrival: float

class ArrivalResponse(BaseModel):
    message: str
    trip_stage: dict
    vehicle_current_mileage: float

class TripArrivalRequest(BaseModel):
    mileage_at_arrival: float

class TripArrivalResponse(BaseModel):
    message: str
    trip_stage: dict
    vehicle_current_mileage: float

class DepartureRequest(BaseModel):
    next_site_id: Optional[int] = None

class DepartureResponse(BaseModel):
    message: str
    trip_stage: dict
    next_site_id: Optional[int] = None
    next_stage_id: Optional[int] = None

class DropEmployeesFromTripRequest(BaseModel):
    employee_ids: List[int]