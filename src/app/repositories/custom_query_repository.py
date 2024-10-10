from sqlalchemy.orm import Session
from typing import Dict, Any, List
from db.query_builder import QueryBuilder
from models.all_models import Driver, User, Tenancy, Department, Unit, Employee, Designation, SRT, Location, Site, WorkPlan, WorkPlanSource, Vehicle, VehicleMaintenance, MaintenanceType, FuelPurchase, Trip, TripReport, ThematicArea, IssueLogSource, IssueStatus, MeetingType, Meeting, IssueLog, ActionPointSource, ActionPoint

class CustomQueryRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.models = {
            'Driver': Driver,
            'User': User,
            'Tenancy': Tenancy,
            'Department': Department,
            'Unit': Unit,
            'Employee': Employee,
            'Designation': Designation,
            'SRT': SRT,
            'Location': Location,
            'Site': Site,
            'WorkPlan': WorkPlan,
            'WorkPlanSource': WorkPlanSource,
            'Vehicle': Vehicle,
            'VehicleMaintenance': VehicleMaintenance,
            'MaintenanceType': MaintenanceType,
            'FuelPurchase': FuelPurchase,
            'Trip': Trip,
            'TripReport': TripReport,
            'ThematicArea': ThematicArea,
            'IssueLogSource': IssueLogSource,
            'IssueStatus': IssueStatus,
            'MeetingType': MeetingType,
            'Meeting': Meeting,
            'IssueLog': IssueLog,
            'ActionPointSource': ActionPointSource,
            'ActionPoint': ActionPoint
        }

    def execute_custom_query(self, model_name: str, columns: Dict[str, List[str]], filters: List[Dict[str, Any]], order_by: List[str], limit: int, offset: int, join_tables: List[str]):
        if model_name not in self.models:
            raise ValueError(f"Unsupported table: {model_name}")
        
        model = self.models[model_name]
        query_builder = QueryBuilder(self.db_session, model)
        
        if join_tables:
            query_builder.join(join_tables)
        
        query_builder.columns(columns).filter(filters).order_by(order_by).limit(limit).offset(offset)
        
        return query_builder.build()
