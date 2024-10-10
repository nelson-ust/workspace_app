# models_metadata.py

from models.all_models import (
    Driver, Tenancy, UserRole, User, Department, Unit, Employee,
    Designation, SRT, Location, Site, WorkPlan, WorkPlanSource, Vehicle,
    VehicleMaintenance, MaintenanceType, FuelPurchase, Trip, TripReport,
    ThematicArea, IssueLogSource, IssueStatus, MeetingType, Meeting,
    IssueLog, ActionPointSource, ActionPoint
)
from sqlalchemy.inspection import inspect

def get_model_metadata():
    models = [
        Driver, Tenancy, UserRole, User, Department, Unit, Employee,
        Designation, SRT, Location, Site, WorkPlan, WorkPlanSource, Vehicle,
        VehicleMaintenance, MaintenanceType, FuelPurchase, Trip, TripReport,
        ThematicArea, IssueLogSource, IssueStatus, MeetingType, Meeting,
        IssueLog, ActionPointSource, ActionPoint
    ]

    metadata = {}
    for model in models:
        columns = [column.name for column in inspect(model).c]
        metadata[model.__tablename__] = columns
    return metadata
