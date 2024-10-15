# init_db.py
from db.database import reset_database, create_tables
from models import all_models
# from models.all_models import User, UserRole, Department, Unit, SRT,Site ,WorkPlan 
# from models.all_models import ApprovalFlow, ApprovalStep, ApprovalLog  # Adjust path as needed
# from models.all_models import PersonalDevelopmentReview  
# from models.all_models import  Vehicle, VehicleMaintenance, MaintenanceType, WorkPlanSource #,RequestStatus
# from models.all_models import FuelPurchase, Driver, Location, Tenancy, Trip,Employee,Designation # , WorkPlanType

def main():
    # Reset the database (drop if exists, then create)
    reset_database()
    
    # Create tables
    create_tables()

if __name__ == "__main__":
    main()
