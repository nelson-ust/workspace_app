
# from sqlalchemy.orm import Session
# from db.database import SessionLocal, create_tables, reset_database
# from repositories.tenancy_repository import TenancyRepository
# from repositories.department_repository import DepartmentRepository
# from repositories.unit_repository import UnitRepository
# from repositories.srt_repository import SRTRepository
# from repositories.employee_repository import EmployeeRepository
# #from repositories.user_role_repository import UserRoleRepository
# from repositories.userRole_repository import UserRoleRepository
# from repositories.user_repository import UserRepository
# from repositories.designation_repository import DesignationRepository
# from schemas.tenancy_schemas import TenancyCreate
# from schemas.department_schemas import DepartmentCreate
# from schemas.unit_schemas import UnitCreate
# from schemas.srt_schemas import SRTCreate
# from schemas.designation_schemas import DesignationCreate
# from schemas.employee_schemas import EmployeeCreate
# from schemas.userRole_schemas import UserRoleCreate
# #from schemas.user_role_schemas import UserRoleCreate
# from schemas.user_schemas import UserCreate, RoleAssignment
# from db.database import get_db
# from auth.security import get_password_hash


# def seed_data(db_session: Session):
#     # Create instances of repositories
#     tenancy_repo = TenancyRepository(db_session)
#     department_repo = DepartmentRepository(db_session)
#     unit_repo = UnitRepository(db_session)
#     srt_repo = SRTRepository(db_session)
#     designation_repo =DesignationRepository(db_session)
#     employee_repo = EmployeeRepository(db_session)
#     user_role_repo = UserRoleRepository(db_session)
#     user_repo = UserRepository(db_session)

#     # Seed Tenancy
#     tenancy_seed = ["Abia", "Enugu", "Imo", "Abuja"]
#     for roles in tenancy_seed:
#         tenancy_data = TenancyCreate(name=roles)
#         tenancy = tenancy_repo.create_tenancy(tenancy_data)

#     # Seed Department
#     department_seed = ["SI", "Admin", "Programs", "Care_and_Treatment", "Grant", "Finance", "Pharmacy", "Laboratory", "OVC", "Prevention"]
#     for roles in department_seed:
#         department_data = DepartmentCreate(name=roles, tenancy_id=tenancy.id)
#         department = department_repo.create_department(department_data)

#     # Seed Unit
#     unit_seed = [["HI", 1],["MEAL", 1], ["QI", 1] , ["Admin", 2], ["Procurement", 2], ["ICT", 2], ["Transport Logistics", 2],
#                 ["Program", 3], ["Care and Treatment", 4], ["Grant", 5], ["Finance", 6], ["Pharmacy", 7], ["Laboratory", 8],
#                 ["OVC_unit", 9], ["Prevention_unit", 10]]
#     for roles in unit_seed:
#         unit_data = UnitCreate(name=roles[0], department_id=roles[1])
#         unit = unit_repo.create_unit(unit_data)

#     # Seed SRT
#     srt_seed = [["SRT A", "Abia SRT A", 1 ], ["SRT B", "Abia SRT B", 1], ["SRT C", "Abia SRT C", 1], ["SRT D", "Abia SRT D", 1],
#                 ["SRT A", "Enugu SRT A", 2 ], ["SRT B", "Enugu SRT B", 2], ["SRT C", "Enugu SRT C", 2], ["SRT D", "Enugu SRT D", 2],
#                 ["SRT A", "Imo SRT A", 3 ], ["SRT B", "Imo SRT B", 3], ["SRT C", "Imo SRT C", 3], ["SRT D", "Imo SRT D", 3]]
#     for roles in srt_seed:
#         srt_data = SRTCreate(name=roles[0], description=roles[1], tenancy_id=roles[2])
#         srt = srt_repo.create_srt(srt_data)

#     # Seed Designation
#     designation_seed = ["Executive Secretary/CEO", "Deputy Executive Secretary", "Chief of Party", "Program Director", "Director", "Associate Director", "Senior Advisor", 
#                         "Advisor", "Senior Specialist/Senior Program Manager", "Specialist/Program Manager","Senior Officer", "Officer", "Associate", "Assistant"]
#     for roles in designation_seed:
#         designation_data =DesignationCreate(name=roles)
#         designation=designation_repo.create_designation(designation_data)

#     # Seed Employee
#     employee_seed = [
#         ["Nelson", "Attah", "07037176436", 1, 1, "CCFN/20221/A664", "Beside Unique Life Hotels", "Abia", "Umuahia", 9, 1]
#         # ["Princess", "Okorie", "08034079732", 1, 3, "CCFN/2021/A623", "Marculey Street Off Azikiwe Str", "Akwa Ibom", "Abak", 9, 2],
#         # ["Tega", "Ekoh", "08032120241", 1, 1, "CCFN/2021/A622", "Along Timber Road", "Delta", "Warri", 8, 4 ],
#         # ["Onyedikachi", "Ezeobi", "08104807107", 1, 1, "CCFN/2021/A665", "Opposite Christ Apostolic Church Amuzukwu", "Abia", "Umuahia", 16, 1],
#         # ["Godwin", "Mbessey", "09038337102", 1, 1, "CCFN/2021/A666", "Opposite Christ Apostolic Church Amuzukwu", "Abia", "Umuahia", 16, 1],
#         # ["Donatus", "Nnadi", "08034000217", 3, 8, "CCFN/2021/A667", "Beside Christ Apostolic Church Afara", "Abia", "Umuahia", 17, 1],
#         # ["Rolex", "Okoh", "08064674737", 1, 1, "CCFN/20221/A668", "Along Panyu Life Hotels", "Enugu", "Enugu North", 12, 2],
#         # ["Fredrick", "Wehzum", "08123563451", 3, 8, "CCFN/2021/A669", "Close to Christ Apostolic Church Emene", "Enugu", "Enugu North", 17, 2],
#         # ["Danjuma", "Alhassan", "08030896097", 1, 1, "CCFN/2021/A670", "Timbers Avenue New Owerri", "Imo", "Owerri North", 12, 3 ],
#         # ["Andrew", "Okeke", "09081048071", 3, 8, "CCFN/2022/A671", "Along All Season Hotel", "Imo", "Owerri North", 17, 3]

#     ]
#     for roles in employee_seed:
#         employee_data = EmployeeCreate(
#             first_name=roles[0], 
#             last_name=roles[1],
#             phone_number=roles[2],
#             department_id=roles[3],
#             unit_id=roles[4],
#             staff_code=roles[5],
#             address=roles[6],
#             state_origin=roles[7],
#             lga_origin=roles[8],
#             designation_id=roles[9],  
#             tenancy_id=roles[10]
#         )
#         employee = employee_repo.create_employee(employee_data)

#     # Seed UserRole
#     role_seed = ["super_admin","tenant_admin","stl","technical_lead", "programs_lead","program_team", "admin_team", "admin_lead","unit_lead", "department_lead", "unit_member","hq_staff"]
#     for roles in role_seed:
#         role_data = UserRoleCreate(name=roles)
#         role = user_role_repo.create_role(role_data)

#     # Seed User
#     user_seed = [
#         ["nelson", "nattah@ccfng.org", "Admin123", 1, 1]
#     #     ["pmarcus", "pmarcus@ccfng.org", "Admin123", 1, 4],
#     #     ["tegaekoh", "tegaekoh@ccfng.org", "Admin123", 2, 4],
#     #     ["onyedikachi", "ocallistus@ccfng.org", "Admin123", 4, 1],
#     #     ["godwin", "godwin@ccfng.org", "Admin123", 5, 1],
#     #     ["donatus", "dnnadi@ccfng.org", "Admin123", 6, 1],
#     #     ["rolex", "rolex@ccfng.org", "Admin123", 7, 2],
#     #     ["fredrick", "fredrick@ccfng.org", "Admin123", 8, 2],
#     #     ["danjuma", "danjuma@ccfng.org", "Admin123", 9, 3],
#     #     ["andrew", "andrew@ccfng.org", "Admin123", 10, 3]
#     ]
#     for roles in user_seed:
#         hashed_password=get_password_hash(roles[2])
#         user_data = UserCreate(
#             username=roles[0],
#             email=roles[1],
#             password=hashed_password,
#             employee_id=roles[3],
#             tenancy_id=roles[4]
#         )
#         user = user_repo.create_user(db_session, user_data)

#     # User Roles
#     user_role = RoleAssignment(user_id=1, roles=[1, 2, 9, 11])
#     roles = user_repo.assign_roles(user_id=user_role.user_id, role_ids=user_role.roles)

#     print(f"Seeded Tenancy: {tenancy.name}")
#     print(f"Seeded Department: {department.name}")
#     print(f"Seeded Unit: {unit.name}")
#     print(f"Seeded SRT: {srt.name}")
#     print(f"Seeded Employee: {employee.first_name} {employee.last_name}")
#     print(f"Seeded Designation: {designation.name}")
#     print(f"Seeded UserRole: {role.name}")
#     print(f"Seeded User: {user.username}")
#     print(f'Seeded User Roles {user.roles}')

# def main():
    
#     # # Reset the database to a clean state before seeding
#     # reset_database()
    
#     # # Create database tables
#     # create_tables()

#     # # Create a new session
#     db_session = SessionLocal()

#     try:
#         seed_data(db_session)
#         db_session.commit()
#         print("Seeding completed successfully.")
#     except Exception as e:
#         print(f"An error occurred while seeding the database: {str(e)}")
#         db_session.rollback()
#     finally:
#         db_session.close()

# if __name__ == "__main__":
#     main()





from sqlalchemy.orm import Session
from db.database import SessionLocal, create_tables, reset_database

from repositories.tenancy_repository import TenancyRepository
from repositories.department_repository import DepartmentRepository
from repositories.unit_repository import UnitRepository
from repositories.srt_repository import SRTRepository
from repositories.employee_repository import EmployeeRepository
#from repositories.user_role_repository import UserRoleRepository
from repositories.userRole_repository import UserRoleRepository
from repositories.user_repository import UserRepository
from repositories.designation_repository import DesignationRepository
from repositories.workplan_repository import WorkPlanRepository
from repositories.workplanSource_repository import WorkPlanSourceRepository
from repositories.location_repository import LocationRepository
from repositories.site_repository import SiteRepository
from repositories.driver_repository import DriverRepository
from repositories.vehicle_repository import VehicleRepository

from schemas.tenancy_schemas import TenancyCreate
from schemas.department_schemas import DepartmentCreate
from schemas.unit_schemas import UnitCreate
from schemas.srt_schemas import SRTCreate
from schemas.designation_schemas import DesignationCreate
from schemas.employee_schemas import EmployeeCreate
from schemas.userRole_schemas import UserRoleCreate
from schemas.workplan_schemas import WorkPlanCreate
from schemas.workplanSource_schemas import WorkPlanSourceCreate
from schemas.location_schemas import LocationCreate
from schemas.site_schemas import SiteCreate
from schemas.driver_schemas import DriverCreate
from schemas.vehicle_schemas import VehicleCreate


#from schemas.user_role_schemas import UserRoleCreate
from schemas.user_schemas import UserCreate, RoleAssignment
from db.database import get_db
from passlib.context import CryptContext
from datetime import datetime
import csv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def read_employee_data_from_csv(csv_file): 
    employee_data = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            name = row[0]
            surname = row[1]
            phone_number = row[2]
            department = row[3]
            unit = row[4]
            staff_id = row[5]
            email_address = row[6]
            address = row[7]
            state_of_origin = row[8]
            lga_of_origin = row[9]
            date_of_birth = row[10]
            position = row[11]
            tenancy_id = row[12]
            password = row[13]
            roles = row[14]
            gender = row[15]

            employee_data.append(
                [name, surname, phone_number, department, unit, staff_id, email_address, address, 
                 state_of_origin, lga_of_origin, date_of_birth, position, tenancy_id, password, roles, gender
                 ]
            )

    return employee_data


def seed_data(db_session: Session, employee_seed:list):
    # Create instances of repositories
    tenancy_repo = TenancyRepository(db_session)
    department_repo = DepartmentRepository(db_session)
    unit_repo = UnitRepository(db_session)
    srt_repo = SRTRepository(db_session)
    designation_repo =DesignationRepository(db_session)
    employee_repo = EmployeeRepository(db_session)
    user_role_repo = UserRoleRepository(db_session)
    user_repo = UserRepository(db_session)
    location_repo = LocationRepository(db_session)
    sites_repo = SiteRepository(db_session)
    workplan_source_repo = WorkPlanSourceRepository(db_session)
    driver_repo = DriverRepository(db_session)
    vehicle_repo = VehicleRepository(db_session)

    
    # Seed Tenancy
    tenancy_seed = ["Abia", "Enugu", "Imo", "Abuja"]
    for roles in tenancy_seed:
        tenancy_data = TenancyCreate(name=roles)
        tenancy = tenancy_repo.create_tenancy(tenancy_data)

    # Seed Department
    department_seed = ["Strategic Information", "Admin", "Programs", "Care and Treatment", "Finance", "Pharmacy", "Laboratory", "Ophans and Vulnerable", "Prevention", "Communication"]
    for roles in department_seed:
        department_data = DepartmentCreate(name=roles, tenancy_id=tenancy.id)
        department = department_repo.create_department(department_data)

    # Seed Unit
    unit_seed = [["Health Informatics Unit", 1], ["Quality Improvement and Surveillance Unit", 1], ["Monitoring and Evaluation Unit", 1], ["Admin Unit", 2], ["Procurement Unit", 2], ["ICT_unit", 2], ["Transport and logistics Unit", 2],
                ["Program Unit", 3], ["Care and Treatment Unit", 4], ["Grant Unit", 5], ["Finance Unit", 5], ["Pharmacy Unit", 6], ["LaboratoryUnit", 7],
                ["Ophans and Vulnerable Unit", 8], ["Prevention Unit", 9], ["Communication", 10]]
    for roles in unit_seed:
        unit_data = UnitCreate(name=roles[0], department_id=roles[1])
        unit = unit_repo.create_unit(unit_data)

    # Seed SRT
    srt_seed = [["SRT A", "Abia SRT A", 1 ], ["SRT B", "Abia SRT B", 1], ["SRT C", "Abia SRT C", 1], ["SRT D", "Abia SRT D", 1],
                ["SRT A", "Enugu SRT A", 2 ], ["SRT B", "Enugu SRT B", 2], ["SRT C", "Enugu SRT C", 2], ["SRT D", "Enugu SRT D", 2],
                ["SRT A", "Imo SRT A", 3 ], ["SRT B", "Imo SRT B", 3], ["SRT C", "Imo SRT C", 3], ["SRT D", "Imo SRT D", 3]]
    for roles in srt_seed:
        srt_data = SRTCreate(name=roles[0], description=roles[1], tenancy_id=roles[2])
        srt = srt_repo.create_srt(srt_data)

    # Seed Designation
    designation_seed = ["Executive Secretary/CEO", "Deputy Executive Secretary", "Chief of Party", "Program Director", "Director", "Associate Director", "Senior Advisor", 
                        "Advisor", "Senior Specialist/Senior Program Manager", "Specialist/Program Manager","Senior Officer", "Officer", "Associate", "Assistant"]
    for roles in designation_seed:
        designation_data =DesignationCreate(name=roles)
        designation=designation_repo.create_designation(designation_data)

    # Seed Employee
    for roles in employee_seed:
        employee_data = EmployeeCreate(
            first_name=roles[0], 
            last_name=roles[1],
            phone_number=roles[2],
            department_id=roles[3],
            unit_id=roles[4],
            staff_code=roles[5],
            employee_email=roles[6],
            address=roles[7],
            state_origin=roles[8],
            lga_origin=roles[9],
            date_of_birth=datetime.strptime(roles[10], "%d/%m/%Y"),
            designation_id=roles[11],  
            tenancy_id=roles[12],
            gender=roles[15]
        )
        employee = employee_repo.create_employee(employee_data)

    # Seed UserRole
    role_seed = ["super_admin","tenant_admin","stl","technical_lead", "programs_lead","program_team", "admin_team", "admin_lead","unit_lead", "department_lead", "unit_member","hq_backstop", "driver", "chief_driver"]
    for roles in role_seed:
        role_data = UserRoleCreate(name=roles)
        role = user_role_repo.create_role(role_data)

    # Seed Location
    location_seed = [
        ["Aba", 1], ["Arochukwu", 1], ["Ohafia", 1], ["Umuahia", 1],
        ["Owerri Municipal", 3], ["Owerri North", 3], ["Orlu", 3], ["Okigwe", 3], ["Ngor Okpala", 3], ["Obowo", 3]
    ]
    for location in location_seed:
        location_data = LocationCreate(name=location[0], tenancy_id=int(location[1]))
        locations = location_repo.create_location(location_data=location_data)


    # Seed WorkPlanSource
    workplan_source_seed = ["Unit", "Department", "SRT", "ThematicArea", "Special Assignments"]
    for source in  workplan_source_seed:
        workplan_source_data = WorkPlanSourceCreate(name=source) 
        workplan_source = workplan_source_repo.create_work_plan_source(work_plan_type_data=workplan_source_data)


    # Seed Sites
    sites_seed = [
        ["Abia State Specialist Hospital, Amachara", "Facility", 1, 4], ["Federal Medical Centre Umuahia", "Facility", 1, 4],
        ["New Era", "Facility", 1, 1], ["Mendel", "Facility", 1, 1],
        ["St Anthony Arochukwu", "Facility", 1, 2], ["General Hospital Arochukwu", "Facility", 1, 2],
        ["General Hospital Ohafia", "Facility", 1, 3], ["King of kings Ohafia", "Facility", 1, 3],
        ["Okigwe General Hospital", "Facility", 3, 8], ["Federal Medical Centre Owerri", "Facility", 3, 5],
        ["Imo State University Teaching Hospital", "Facility", 3, 7], ["St Damian Catholic Hospital", "Facility", 3, 7],
        ["Imo State Specialist Hospital", "Facility", 3, 5], ["Holy Rosary Hospital Emekuku", "Facility", 3, 6],
        ["Ngor Okpala General Hospital", "Facility", 3, 9], ["Our Lady of Mercy, Obowo", "Facility", 3, 10]
    ]
    for sites in sites_seed:
        sites_data = SiteCreate(
            name=sites[0], site_type=sites[1], tenancy_id=sites[2], location_id=sites[3]
        )
        sites_create = sites_repo.create_site(site_data=sites_data)


    # Seed User
    employee_no = 1
    for roles in employee_seed:
        hashed_password='Admin123'
        user_data = UserCreate(
            username=roles[0],
            email=roles[6],
            password=hashed_password,
            employee_id=employee_no,
            tenancy_id=roles[12]
        )
        user = user_repo.create_user(db_session, user_data)
        employee_no+=1


    # User Roles
    user_no = 1
    for roles in employee_seed:
        roles = (roles[14]).split(sep=', ')
        user_role = RoleAssignment(user_id=user_no, roles=roles)
        roles = user_repo.assign_roles(user_id=user_role.user_id, role_ids=user_role.roles)
        user_no+=1

    ## Seed Drivers
    drivers_data = [
        [51, "ABI00000001", "2025-02-01", 1,True],
        [52, "ABI00000002", "2024-12-12", 1,True],
        [53, "ABI00000003", "2024-12-05", 1,True],
        [54, "ABI00000004", "2025-01-25", 1,True],
        [55, "ABI00000005", "2025-01-25", 1,True],
        [56, "ABI00000006", "2025-01-25", 1,True],
        [57, "ABI00000007", "2025-01-25", 1,True],
        [58, "ABI00000008", "2025-01-25", 1,True],
        [59, "ABI00000009", "2025-01-25", 1,True],
        [60, "ABI00000010", "2025-01-25", 1,True],
        [61, "ABI00000011", "2025-01-25", 1,True],
        [62, "ABI00000012", "2025-01-25", 1,True],
        [105, "ABI00000013", "2025-01-25", 3,True],
        [106, "ABI00000014", "2025-01-25", 3,True],
        [107, "ABI00000015", "2025-01-25", 3,True],
        [108, "ABI00000016", "2025-01-25", 3,True],
        [109, "ABI00000017", "2025-01-25", 3,True],
        [110, "ABI00000018", "2025-01-25", 3,True],
        [111, "ABI00000019", "2025-01-25", 3,True],
        [112, "ABI00000020", "2025-01-25", 3,True],
        [113, "ABI00000021", "2025-01-25", 3,True],
        [114, "ABI00000022", "2025-01-25", 3,True]
    ]
    for driver in drivers_data:
        driver_info = DriverCreate(user_id=driver[0], 
                                   licence_number=driver[1], 
                                   licence_exp_date=driver[2], 
                                   tenancy_id=driver[3],
                                   is_available=driver[4]
        )
        drivers_create = driver_repo.create_driver(driver_data=driver_info)


    ## Seed Vehicles
    vehicles_data = [
        ["White Bus", "32J321FG", "ABU101", "Toyota", 2018, "Petrol", 270, 16, 1],
        ["4Runner Jeep", "12R890FG", "ABU102", "Toyota", 2017, "Petrol", 280, 4, 1],
        ["4Runner Jeep", "32J211FG", "ABU103", "Toyota", 2016, "Petrol", 280, 4, 1],
        ["White Bus", "12R933FG", "ABU104", "Toyota", 2019, "Petrol", 270, 16, 1],
        ["4Runner Jeep", "32J111FG", "ABU105", "Toyota", 2019, "Petrol", 280, 4, 1],
        ["Prado Jeep", "32J318FG", "ABI106", "Toyota", 2019, "Petrol", 285, 6, 1],
        ["White Bus", "32J321IM", "ABU106", "Toyota", 2018, "Petrol", 270, 16, 2],
        ["4Runner Jeep", "12R890IM", "ABU107", "Toyota", 2017, "Petrol", 280, 4, 2],
        ["4Runner Jeep", "32J211IM", "ABU108", "Toyota", 2016, "Petrol", 280, 4, 2],
        ["White Bus", "12R933IM", "ABU109", "Toyota", 2019, "Petrol", 270, 16, 2],
        ["4Runner Jeep", "32J111IM", "ABU110", "Toyota", 2019, "Petrol", 280, 4, 2],
        ["Prado Jeep", "32J318IM", "ABI111", "Toyota", 2019, "Petrol", 285, 6, 2]
    ]
    for vehicles in vehicles_data:
        vehicle_info = VehicleCreate(name=vehicles[0],
                                     licence_plate=vehicles[1],
                                     alternate_plate=vehicles[2],
                                     make=vehicles[3],
                                     year=vehicles[4],
                                     fuel_type=vehicles[5],
                                     current_mileage=vehicles[6],
                                     seat_capacity=vehicles[7],
                                     tenancy_id=vehicles[8]
                                )
        vehicle_create = vehicle_repo.create_vehicle(vehicle_info=vehicle_info)




    print(f"Seeded Tenancy: {tenancy.name}")
    print(f"Seeded Department: {department.name}")
    print(f"Seeded Unit: {unit.name}")
    print(f"Seeded SRT: drivers{srt.name}")
    print(f"Seeded Employee: {employee.first_name} {employee.last_name}")
    print(f"Seeded Designation: {designation.name}")
    print(f"Seeded UserRole: {role.name}")
    print(f"Seeded User: {user.username}")
    print(f'Seeded User Roles {user.roles}')
    print(f'Seeded Location {locations.name}')
    print(f'Seeded WorkPlanSoource {workplan_source.name}')
    print(f'Seeded Sites {sites_create.name}')
   # print(f'Seeded Workplan {workplan.specific_task}')


def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

def main():
    # # Create database tables
    # create_tables()

    # # Reset the database to a clean state before seeding
    # reset_database()

    # # Create a new session
    db_session = SessionLocal()

    try:
        csv_file = 'src/staff_directory.csv'
        employee_seed = read_employee_data_from_csv(csv_file=csv_file)
        seed_data(db_session, employee_seed)
        db_session.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        print(f"An error occurred while seeding the database: {str(e)}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == "__main__":
    main()




# from sqlalchemy.orm import Session
# from db.database import SessionLocal, create_tables, reset_database

# from repositories.tenancy_repository import TenancyRepository
# from repositories.department_repository import DepartmentRepository
# from repositories.unit_repository import UnitRepository
# from repositories.srt_repository import SRTRepository
# from repositories.employee_repository import EmployeeRepository
# #from repositories.user_role_repository import UserRoleRepository
# from repositories.userRole_repository import UserRoleRepository
# from repositories.user_repository import UserRepository
# from repositories.designation_repository import DesignationRepository
# from repositories.workplan_repository import WorkPlanRepository
# from repositories.workplanSource_repository import WorkPlanSourceRepository
# from repositories.location_repository import LocationRepository
# from repositories.site_repository import SiteRepository
# from repositories.driver_repository import DriverRepository
# from repositories.vehicle_repository import VehicleRepository

# from schemas.tenancy_schemas import TenancyCreate
# from schemas.department_schemas import DepartmentCreate
# from schemas.unit_schemas import UnitCreate
# from schemas.srt_schemas import SRTCreate
# from schemas.designation_schemas import DesignationCreate
# from schemas.employee_schemas import EmployeeCreate
# from schemas.userRole_schemas import UserRoleCreate
# from schemas.workplan_schemas import WorkPlanCreate
# from schemas.workplanSource_schemas import WorkPlanSourceCreate
# from schemas.location_schemas import LocationCreate
# from schemas.site_schemas import SiteCreate
# from schemas.driver_schemas import DriverCreate
# from schemas.vehicle_schemas import VehicleCreate


# #from schemas.user_role_schemas import UserRoleCreate
# from schemas.user_schemas import UserCreate, RoleAssignment
# from db.database import get_db
# from passlib.context import CryptContext
# from datetime import datetime

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def seed_data(db_session: Session):
#     # Create instances of repositories
#     tenancy_repo = TenancyRepository(db_session)
#     department_repo = DepartmentRepository(db_session)
#     unit_repo = UnitRepository(db_session)
#     srt_repo = SRTRepository(db_session)
#     designation_repo =DesignationRepository(db_session)
#     employee_repo = EmployeeRepository(db_session)
#     user_role_repo = UserRoleRepository(db_session)
#     user_repo = UserRepository(db_session)
#     location_repo = LocationRepository(db_session)
#     sites_repo = SiteRepository(db_session)
#     workplan_source_repo = WorkPlanSourceRepository(db_session)
#     workplan_repo = WorkPlanRepository(db_session)
#     driver_repo = DriverRepository(db_session)
#     vehicle_repo = VehicleRepository(db_session)

#     # Seed Tenancy
#     tenancy_seed = ["Abia", "Enugu", "Imo", "Abuja"]
#     for roles in tenancy_seed:
#         tenancy_data = TenancyCreate(name=roles)
#         tenancy = tenancy_repo.create_tenancy(tenancy_data)

#     # Seed Department
#     department_seed = ["SI", "Admin", "Programs", "Care_and_Treatment", "Grant", "Finance", "Pharmacy", "Laboratory", "OVC", "Prevention"]
#     for roles in department_seed:
#         department_data = DepartmentCreate(name=roles, tenancy_id=tenancy.id)
#         department = department_repo.create_department(department_data)

#     # Seed Unit
#     unit_seed = [["HI_unit", 1], ["QI_unit", 1], ["MEAL_unit", 1], ["Admin_unit", 2], ["Procurement_unit", 2], ["ICT_unit", 2], ["Transport_logistics_unit", 2],
#                 ["Program_unit", 3], ["Care_and_Treatment_unit", 4], ["Grant_unit", 5], ["Finance_unit", 6], ["Pharmacy_unit", 7], ["Laboratory_unit", 8],
#                 ["OVC_unit", 9], ["Prevention_unit", 10]]
#     for roles in unit_seed:
#         unit_data = UnitCreate(name=roles[0], department_id=roles[1])
#         unit = unit_repo.create_unit(unit_data)

#     # Seed SRT
#     srt_seed = [["SRT A", "Abia SRT A", 1 ], ["SRT B", "Abia SRT B", 1], ["SRT C", "Abia SRT C", 1], ["SRT D", "Abia SRT D", 1],
#                 ["SRT A", "Enugu SRT A", 2 ], ["SRT B", "Enugu SRT B", 2], ["SRT C", "Enugu SRT C", 2], ["SRT D", "Enugu SRT D", 2],
#                 ["SRT A", "Imo SRT A", 3 ], ["SRT B", "Imo SRT B", 3], ["SRT C", "Imo SRT C", 3], ["SRT D", "Imo SRT D", 3]]
#     for roles in srt_seed:
#         srt_data = SRTCreate(name=roles[0], description=roles[1], tenancy_id=roles[2])
#         srt = srt_repo.create_srt(srt_data)

#     # Seed Designation
#     designation_seed = ["Executive Secretary/CEO", "Deputy Executive Secretary", "Chief of Party", "Program Director", "Director", "Associate Director", "Senior Advisor", 
#                         "Advisor", "Senior Specialist/Senior Program Manager", "Specialist/Program Manager","Senior Officer", "Officer", "Associate", "Assistant"]
#     for roles in designation_seed:
#         designation_data =DesignationCreate(name=roles)
#         designation=designation_repo.create_designation(designation_data)

#     # Seed Employee
#     employee_seed = [
#         ["Nelson", "Attah", "07037176436", 1, 1, "CCFN/20221/A664","nattah@ccfng.org", "Beside Unique Life Hotels", "Abia", "Umuahia", 9, 1],
#         ["Princess", "Okorie", "08034079732", 1, 3, "CCFN/2021/A623","pokorie@ccfng.org", "Marculey Street Off Azikiwe Str", "Akwa Ibom", "Abak", 4, 4],
#         ["Tega", "Ekoh", "08032120241", 1, 1, "CCFN/2021/A622","tegaekoh@ccfng.org", "Along Timber Road", "Delta", "Warri", 8, 4 ],
#         ["Onyedikachi", "Ezeobi", "08104807107", 1, 1, "CCFN/2021/A665","ocallistus@ccfng.org", "Opposite Christ Apostolic Church Amuzukwu", "Abia", "Umuahia", 14, 1],
#         ["Godwin", "Mbessey", "09038337102", 1, 1, "CCFN/2021/A666","maondohemba@ccfng.org", "Opposite Christ Apostolic Church Amuzukwu", "Abia", "Umuahia", 14, 1],
#         ["Donatus", "Nnadi", "08034000217", 3, 8, "CCFN/2021/A667","dnnadi@ccfng.org", "Beside Christ Apostolic Church Afara", "Abia", "Umuahia", 10, 1],
#         ["Rolex", "Okoh", "08064674737", 1, 1, "CCFN/20221/A668","jamesokoh@ccfng.org", "Along Panyu Life Hotels", "Enugu", "Enugu North", 12, 2],
#         ["Fredrick", "Wehzum", "08123563451", 3, 8, "CCFN/2021/A669","fwhezum@ccfng.org", "Close to Christ Apostolic Church Emene", "Enugu", "Enugu North", 12, 2],
#         ["Danjuma", "Alhassan", "08030896097", 1, 1, "CCFN/2021/A670","adanjuma@ccfng.org", "Timbers Avenue New Owerri", "Imo", "Owerri North", 12, 3 ],
#         ["Andrew", "Okeke", "09081048071", 3, 8, "CCFN/2022/A671","tabba@ccfng.org", "Along All Season Hotel", "Imo", "Owerri North", 10, 3],
#         ["Okon", "Eyo", "08093203616", 2, 7, "CCFN/2015/A570", "oeyo@ccfng.org", "Beside Primary School, Amachara", "Akwa Ibom", "Isam", 14, 1],
#         ["John", "Ejiadu", "08066822295", 2, 7, "CCFN/2018/A571", "jejiadu@ccfng.org", "Along Besala Road, Ahiaeke", "Benue", "Otukpo", 14, 1],
#         ["Ernest", "Ugwu", "08030980608", 2, 7, "CCFN/2018/A572", "eugwu@ccfng.org", "Opposite Christ Assemble Church, Uwgueke", "Enugu", "Nsukka", 14, 1],
#         ["Chidozie", "Uzoigwe", "07012701680", 2, 7, "CCFN/2019/A573", "cuzoigwe@ccfng.org", "No. 15 Bandela Street, Beside High Court, Ibeku", "Abia", "Ohafia", 14, 1]

#     ]
#     for roles in employee_seed:
#         employee_data = EmployeeCreate(
#             first_name=roles[0], 
#             last_name=roles[1],
#             phone_number=roles[2],
#             department_id=roles[3],
#             unit_id=roles[4],
#             staff_code=roles[5],
#             employee_email=roles[6],
#             address=roles[7],
#             state_origin=roles[8],
#             lga_origin=roles[9],
#             designation_id=roles[10],  
#             tenancy_id=roles[11]
#         )
#         employee = employee_repo.create_employee(employee_data)

#     # Seed UserRole
#     role_seed = ["super_admin","tenant_admin","stl","technical_lead", "programs_lead","program_team", "admin_team", "admin_lead","unit_lead", "department_lead", "unit_member","hq_staff", "driver", "chief_driver"]
#     for roles in role_seed:
#         role_data = UserRoleCreate(name=roles)
#         role = user_role_repo.create_role(role_data)

#     # Seed Location
#     location_seed = [
#         ["Aba", 1], ["Arochukwu", 1], ["Ohafia", 1], ["Umuahia", 1]
#     ]
#     for location in location_seed:
#         location_data = LocationCreate(name=location[0], tenancy_id=int(location[1]))
#         locations = location_repo.create_location(location_data=location_data)


#     # Seed WorkPlanSource
#     workplan_source_seed = ["Unit", "Department", "SRT", "ThematicArea", "Special Assignments"]
#     for source in  workplan_source_seed:
#         workplan_source_data = WorkPlanSourceCreate(name=source) 
#         workplan_source = workplan_source_repo.create_work_plan_source(work_plan_type_data=workplan_source_data)


#     # Seed Sites
#     sites_seed = [
#         ["Abia State Specialist Hospital, Amachara", "Facility", 1, 4], ["Federal Medical Centre", "Facility", 1, 4],
#         ["New Era", "Facility", 1, 1], ["Mendel", "Facility", 1, 1],
#         ["St Anthony Arochukwu", "Facility", 1, 2], ["General Hospital Arochukwu", "Facility", 1, 2],
#         ["General Hospital Ohafia", "Facility", 1, 3], ["King of kings Ohafia", "Facility", 1, 3]
#     ]
#     for sites in sites_seed:
#         sites_data = SiteCreate(
#             name=sites[0], site_type=sites[1], tenancy_id=sites[2], location_id=sites[3]
#         )
#         sites_create = sites_repo.create_site(site_data=sites_data)


#     # Seed User
#     user_seed = [
#         ["nelson", "nattah@ccfng.org", "Admin123", 1, 1],
#         ["princess", "pokorie@ccfng.org", "Admin123", 2, 1],
#         ["tegaekoh", "tegaekoh@ccfng.org", "Admin123", 3, 4],
#         ["onyedikachi", "ocallistus@ccfng.org", "Admin123", 4, 1],
#         ["godwin", "godwin@ccfng.org", "Admin123", 5, 1],
#         ["donatus", "dnnadi@ccfng.org", "Admin123", 6, 1],
#         ["rolex", "rolex@ccfng.org", "Admin123", 7, 2],
#         ["fredrick", "fredrick@ccfng.org", "Admin123", 8, 2],
#         ["danjuma", "danjuma@ccfng.org", "Admin123", 9, 3],
#         ["andrew", "andrew@ccfng.org", "Admin123", 10, 3],
#         ["okon", "oeyo@ccfng.org", "Admin123", 11, 1],
#         ["john", "jejiadu@ccfng.org", "Admin123", 12, 1],
#         ["ernest", "eugwu@ccfng.org", "Admin123", 13, 1],
#         ["chidozie", "cuzoigwe@ccfng.org", "Admin123", 14, 1]
#     ]
#     for roles in user_seed:
#         hashed_password=get_password_hash('Admin123')
#         user_data = UserCreate(
#             username=roles[0],
#             email=roles[1],
#             password=hashed_password,
#             employee_id=roles[3],
#             tenancy_id=roles[4]
#         )
#         user = user_repo.create_user(db_session, user_data)

#     # User Roles
#     user_roles = [
#         [1, [1, 2, 9, 11]], [4, [2, 11]], [11, [7, 11, 13, 14]], 
#         [12, [7, 11, 13]], [7, [7, 11, 13]], [14, [7, 11, 13]]
#     ]
#     for user_id, roles in user_roles:
#         user_role = RoleAssignment(user_id=user_id, roles=roles)
#         roles = user_repo.assign_roles(user_id=user_role.user_id, role_ids=user_role.roles)

#     ## Seed Drivers
#     drivers_data = [
#         [11, "ABI00000001", "2025-02-01", 1,True],
#         [12, "ABI00000002", "2024-12-12", 1,True],
#         [13, "ABI00000003", "2024-12-05", 1,True],
#         [14, "ABI00000004", "2025-01-25", 1,True]
#     ]
#     for driver in drivers_data:
#         driver_info = DriverCreate(user_id=driver[0], 
#                                    licence_number=driver[1], 
#                                    licence_exp_date=driver[2], 
#                                    tenancy_id=driver[3],
#                                    is_available=driver[4]
#         )
#         drivers_create = driver_repo.create_driver(driver_data=driver_info)


#     ## Seed Vehicles
#     vehicles_data = [
#         ["White Bus", "32J321FG", "ABU101", "Toyota", 2018, "Petrol", 270, 16, 1],
#         ["4Runner Jeep", "12R890FG", "ABU102", "Toyota", 2017, "Petrol", 280, 4, 1],
#         ["4Runner Jeep", "32J211FG", "ABU103", "Toyota", 2016, "Petrol", 280, 4, 1],
#         ["White Bus", "12R933FG", "ABU104", "Toyota", 2019, "Petrol", 270, 16, 1],
#         ["4Runner Jeep", "32J111FG", "ABU105", "Toyota", 2019, "Petrol", 280, 4, 1],
#         ["Prado Jeep", "32J318FG", "ABI106", "Toyota", 2019, "Petrol", 285, 6, 1]
#     ]
#     for vehicles in vehicles_data:
#         vehicle_info = VehicleCreate(name=vehicles[0],
#                                      licence_plate=vehicles[1],
#                                      alternate_plate=vehicles[2],
#                                      make=vehicles[3],
#                                      year=vehicles[4],
#                                      fuel_type=vehicles[5],
#                                      current_mileage=vehicles[6],
#                                      seat_capacity=vehicles[7],
#                                      tenancy_id=vehicles[8]
#                                 )
#         vehicle_create = vehicle_repo.create_vehicle(vehicle_info=vehicle_info)




#     print(f"Seeded Tenancy: {tenancy.name}")
#     print(f"Seeded Department: {department.name}")
#     print(f"Seeded Unit: {unit.name}")
#     print(f"Seeded SRT: drivers{srt.name}")
#     print(f"Seeded Employee: {employee.first_name} {employee.last_name}")
#     print(f"Seeded Designation: {designation.name}")
#     print(f"Seeded UserRole: {role.name}")
#     print(f"Seeded User: {user.username}")
#     print(f'Seeded User Roles {user.roles}')
#     print(f'Seeded Location {locations.name}')
#     print(f'Seeded WorkPlanSoource {workplan_source.name}')
#     print(f'Seeded Sites {sites_create.name}')
#    # print(f'Seeded Workplan {workplan.specific_task}')


# def get_password_hash(password: str) -> str:
#         return pwd_context.hash(password)

# def main():
#     # # Create database tables
#     # create_tables()

#     # # Reset the database to a clean state before seeding
#     # reset_database()

#     # # Create a new session
#     db_session = SessionLocal()

#     try:
#         seed_data(db_session)
#         db_session.commit()
#         print("Seeding completed successfully.")
#     except Exception as e:
#         print(f"An error occurred while seeding the database: {str(e)}")
#         db_session.rollback()
#     finally:
#         db_session.close()

# if __name__ == "__main__":
#     main()
