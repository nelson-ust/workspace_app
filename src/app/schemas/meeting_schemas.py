# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime
# from enum import Enum
# #from models.all_models import MeetingCategory

# # class MeetingCreate(BaseModel):
# #     name: str = Field(..., description="The name of the meeting")
# #     date_held: datetime.datetime = Field(..., description="The date and time when the meeting is held")
# #     meeting_type_id: int = Field(..., description="The ID of the meeting type")
# #     organizer_id: int = Field(..., description="The ID of the organizer")
# #     meeting_category: MeetingCategory = Field(..., description="The category of the meeting, e.g., 'PHYSICAL' or 'VIRTUAL'")
# #     is_meal_required: bool = Field(..., description="Indicates if a meal is required")
# #     is_third_party_required: bool = Field(..., description="Indicates if third-party participation is required")

# class MeetingCategoryEnum(str, Enum):
#     VIRTUAL = "VIRTUAL"
#     PHYSICAL = "PHYSICAL"

# class MeetingCreate(BaseModel):
#     name: str
#     date_held: datetime
#     meeting_type_id: int
#     organizer_id: Optional[int] = None
#     meeting_category: MeetingCategoryEnum
#     is_meal_required: bool
#     is_third_party_required: bool

#     class Config:
#         orm_mode = True

# class MeetingUpdate(BaseModel):
#     name: Optional[str]
#     date_held: Optional[datetime]
#     meeting_type_id: Optional[int]
#     organizer_id: Optional[int]
#     meeting_category: Optional[MeetingCategoryEnum]
#     is_meal_required: Optional[bool]
#     is_third_party_required: Optional[bool]

#     class Config:
#         orm_mode = True
# class MealSelectionCreate(BaseModel):
#     selection_type: str = Field(..., description="The type of meal selection")
#     meal_combination_id: int = Field(..., description="The ID of the meal combination")
#     employee_id: Optional[int] = Field(None, description="The ID of the employee")
#     third_party_participant_id: Optional[int] = Field(None, description="The ID of the third-party participant")

# class ParticipantCreate(BaseModel):
#     participant_type: str = Field(..., description="The type of participant")
#     employee_id: Optional[int] = Field(None, description="The ID of the employee")
#     third_party_participant_id: Optional[int] = Field(None, description="The ID of the third-party participant")

# class MeetingMinutesCreate(BaseModel):
#     content: str = Field(..., description="The content of the meeting minutes")

# class AttendanceCreate(BaseModel):
#     participant_type: str = Field(..., description="The type of participant")
#     employee_id: Optional[int] = Field(None, description="The ID of the employee")
#     third_party_participant_id: Optional[int] = Field(None, description="The ID of the third-party participant")
#     attended: bool = Field(False, description="Indicates if the participant attended the meeting")

# class MeetingResponse(BaseModel):
#     id: int
#     name: str
#     date_held: datetime
#     meeting_type_id: int
#     organizer_id: int
#     meeting_category: str
#     is_meal_required: bool
#     is_third_party_required: bool

#     class Config:
#         orm_mode = True

# class MealSelectionResponse(BaseModel):
#     id: int
#     meeting_id: int
#     selection_type: str
#     meal_combination_id: int
#     employee_id: Optional[int]
#     third_party_participant_id: Optional[int]

#     class Config:
#         orm_mode = True

# class ParticipantResponse(BaseModel):
#     id: int
#     meeting_id: int
#     participant_type: str
#     employee_id: Optional[int]
#     third_party_participant_id: Optional[int]

#     class Config:
#         orm_mode = True

# class MeetingMinutesResponse(BaseModel):
#     id: int
#     meeting_id: int
#     content: str

#     class Config:
#         orm_mode = True

# class AttendanceResponse(BaseModel):
#     id: int
#     meeting_id: int
#     participant_type: str
#     employee_id: Optional[int]
#     third_party_participant_id: Optional[int]
#     attended: bool

#     class Config:
#         orm_mode = True

# class MeetingTypeResponse(BaseModel):
#     id: int
#     name: str

#     class Config:
#         orm_mode = True

# class CompanyResponse(BaseModel):
#     id: int
#     name: str

#     class Config:
#         orm_mode = True

# class MealCombinationResponse(BaseModel):
#     id: int
#     name: str

#     class Config:
#         orm_mode = True



from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MeetingCreate(BaseModel):
    name: str
    date_start: datetime
    date_end: datetime
    meeting_type_id: int
    organizer_id: int
    meeting_category: str
    is_meal_required: bool
    is_third_party_required: bool

    class Config:
        orm_mode = True

class MeetingUpdate(BaseModel):
    name: Optional[str]
    date_start: Optional[datetime]
    date_end: Optional[datetime]
    meeting_type_id: Optional[int]
    organizer_id: Optional[int]
    meeting_category: Optional[str]
    is_meal_required: Optional[bool]
    is_third_party_required: Optional[bool]

    class Config:
        orm_mode = True

class MealSelectionCreate(BaseModel):
    selection_type: str
    meal_combination_id: int
    employee_id: Optional[int]
    third_party_participant_id: Optional[int]

    class Config:
        orm_mode = True

class ParticipantCreate(BaseModel):
    participant_type: str
    employee_id: Optional[int]
    third_party_participant_id: Optional[int]

    class Config:
        orm_mode = True

class MeetingMinutesCreate(BaseModel):
    content: str

    class Config:
        orm_mode = True

class AttendanceCreate(BaseModel):
    participant_type: str
    employee_id: Optional[int]
    third_party_participant_id: Optional[int]
    attended: bool

    class Config:
        orm_mode = True

class MeetingResponse(BaseModel):
    id: int
    name: str
    date_start: datetime
    date_end: datetime
    meeting_type_id: int
    organizer_id: int
    meeting_category: str
    is_meal_required: bool
    is_third_party_required: bool

    class Config:
        orm_mode = True

class MealSelectionResponse(BaseModel):
    id: int
    selection_type: str
    meal_combination_id: int
    employee_id: Optional[int]
    third_party_participant_id: Optional[int]

    class Config:
        orm_mode = True

class ParticipantResponse(BaseModel):
    id: int
    participant_type: str
    employee_id: Optional[int]
    third_party_participant_id: Optional[int]

    class Config:
        orm_mode = True

class MinutesResponse(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True

class AttendanceResponse(BaseModel):
    id: int
    participant_type: str
    employee_id: Optional[int]
    third_party_participant_id: Optional[int]
    attended: bool

    class Config:
        orm_mode = True
