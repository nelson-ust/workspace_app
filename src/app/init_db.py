# init_db.py
from db.database import reset_database, create_tables
from models.all_models import User, UserRole, Department, Unit, SRT,Site ,WorkPlan #, WorkPlanRequest
from models.all_models import  Vehicle, VehicleMaintenance, MaintenanceType, WorkPlanSource #,RequestStatus
from models.all_models import FuelPurchase, Driver, Location, Tenancy, Trip,Employee,Designation # , WorkPlanType

def main():
    # Reset the database (drop if exists, then create)
    reset_database()
    
    # Create tables
    create_tables()

if __name__ == "__main__":
    main()
