
from sqlalchemy.orm import Session, configure_mappers
from db.database import SessionLocal
from repositories.tenancy_repository import TenancyRepository
from repositories.department_repository import DepartmentRepository
from repositories.unit_repository import UnitRepository
from repositories.srt_repository import SRTRepository
from repositories.employee_repository import EmployeeRepository
from repositories.userRole_repository import UserRoleRepository
from repositories.user_repository import UserRepository
from repositories.designation_repository import DesignationRepository
from repositories.workplanSource_repository import WorkPlanSourceRepository
from repositories.location_repository import LocationRepository
from repositories.site_repository import SiteRepository
from repositories.driver_repository import DriverRepository
from repositories.vehicle_repository import VehicleRepository
from repositories.actionPointSource_repository import ActionPointSourceRepository
from repositories.issue_status_repository import IssueStatusRepository
from repositories.issueLogSource_repository import IssueLogSourceRepository
from repositories.maintenancetype_repository import MaintenanceTypeRepository
from repositories.task_status_repository import TaskStatusRepository
from repositories.meal_combination_repository import MealCombinationRepository
from repositories.company_repository import CompanyRepository
from repositories.meeting_type_repository import MeetingTypeRepository
from repositories.meeting_repository import MeetingRepository
from repositories.thematic_area_repository import ThematicAreaRepository
from repositories.project_repository import ProjectRepository
from repositories.project_component_repository import ProjectComponentRepository
from repositories.funder_repository import FunderRepository
from repositories.funding_repository import FundingRepository
from repositories.document_type_repository import DocumentTypeRepository
from repositories.trip_special_location_repository import TripSpecialLocationRepository

from schemas.tenancy_schemas import TenancyCreate
from schemas.department_schemas import DepartmentCreate
from schemas.unit_schemas import UnitCreate
from schemas.srt_schemas import SRTCreate
from schemas.designation_schemas import DesignationCreate
from schemas.employee_schemas import EmployeeCreate
from schemas.userRole_schemas import UserRoleCreate
from schemas.workplanSource_schemas import WorkPlanSourceCreate
from schemas.location_schemas import LocationCreate
from schemas.site_schemas import SiteCreate
from schemas.driver_schemas import DriverCreate
from schemas.vehicle_schemas import VehicleCreate
from schemas.user_schemas import UserCreate, RoleAssignment
from schemas.actionPointSource_schemas import ActionPointSourceCreate
from schemas.issue_status_schemas import IssueStatusCreate
from schemas.issueLogSource_schemas import IssueLogSourceCreate
from schemas.maintenancetype_schemas import MaintenanceCreate
from schemas.task_status_schemas import TaskStatusCreate
from schemas.company_schemas import CompanyCreate
from schemas.meal_combination_schemas import MealCombinationCreate
from schemas.meeting_type_schemas import MeetingTypeCreate
from schemas.meeting_schemas import MeetingCreate
from schemas.thematic_area_schemas import ThematicAreaCreate
from schemas.project_schemas import ProjectCreate
from schemas.project_component_shemas import ProjectComponentCreate
from schemas.funder_schemas import FunderCreate
from schemas.funding_schemas import FundingCreate
from schemas.trip_special_location_schemas import TripStartLocationCreate
from schemas.document_type_schemas import DocumentTypeCreate

from passlib.context import CryptContext
from datetime import datetime, timedelta
import csv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

configure_mappers()

def read_employee_data_from_csv(csv_file):
    employee_data = []

    with open(csv_file, "r") as file:
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
                [
                    name,
                    surname,
                    phone_number,
                    department,
                    unit,
                    staff_id,
                    email_address,
                    address,
                    state_of_origin,
                    lga_of_origin,
                    date_of_birth,
                    position,
                    tenancy_id,
                    password,
                    roles,
                    gender,
                ]
            )

    return employee_data

def seed_data(db_session: Session, employee_seed: list):
    # Create instances of repositories
    tenancy_repo = TenancyRepository(db_session)
    department_repo = DepartmentRepository(db_session)
    unit_repo = UnitRepository(db_session)
    srt_repo = SRTRepository(db_session)
    designation_repo = DesignationRepository(db_session)
    employee_repo = EmployeeRepository(db_session)
    user_role_repo = UserRoleRepository(db_session)
    user_repo = UserRepository(db_session)
    location_repo = LocationRepository(db_session)
    sites_repo = SiteRepository(db_session)
    workplan_source_repo = WorkPlanSourceRepository(db_session)
    driver_repo = DriverRepository(db_session)
    vehicle_repo = VehicleRepository(db_session)
    action_point_source_repo = ActionPointSourceRepository(db_session)
    issue_status_repo = IssueStatusRepository(db_session)
    issue_log_source_repo = IssueLogSourceRepository(db_session)
    maintenance_type_repo = MaintenanceTypeRepository(db_session)
    task_status_repo = TaskStatusRepository(db_session)
    meal_combination_repo = MealCombinationRepository(db_session)
    company_repo = CompanyRepository(db_session)
    meeting_type_repo = MeetingTypeRepository(db_session)
    meeting_repo = MeetingRepository(db_session)
    thematic_area_repo = ThematicAreaRepository(db_session)
    project_repo = ProjectRepository(db_session)
    project_component_repo = ProjectComponentRepository(db_session)
    funders_repo = FunderRepository(db_session)
    funding_repo = FundingRepository(db_session)
    document_type_repo = DocumentTypeRepository(db_session)
    trip_special_location_repo = TripSpecialLocationRepository(db_session)

    # # Seed Project
    project_seed = [
        ["ACCESS Project Year One", "ACCESS Project Year One", (datetime.strptime("01/10/2022", "%d/%m/%Y")).date(), (datetime.strptime("30/09/2023", "%d/%m/%Y")).date(), 3400000], 
        ["ACCESS Project Year Two", "ACCESS Project Year Two", (datetime.strptime("01/10/2023", "%d/%m/%Y")).date(), (datetime.strptime("30/09/2024", "%d/%m/%Y")).date(), 3400000], 
        ["Global Fund TB Project Year One", "Global Fund TB Project Year One", (datetime.strptime("01/10/2019", "%d/%m/%Y")).date(), None, 20000000], 
        ["Institutional Capacity Strengthening Project", "Institutional Capacity Strengthening", (datetime.strptime("01/10/2020", "%d/%m/%Y")).date(), None, 50000000],
        ["Agriculture and Livelihoods Project", "Agriculture and Livelihoods Project Year", (datetime.strptime("01/10/2022", "%d/%m/%Y")).date(), None, 10000000],
        ["Anti Human Trafficking and Migration Project", "Anti Human Trafficking and Migration Project Year", (datetime.strptime("01/10/2015", "%d/%m/%Y")).date(), None, 15000000],
        ["Good Governance Project Year", "Good Governance Project", (datetime.strptime("01/10/2017", "%d/%m/%Y")).date(), None, 25000000 ]
    ]
    for project_item in project_seed:
        project_data = ProjectCreate(name=project_item[0], description=project_item[1], start_date=project_item[2], end_date=project_item[3], project_sum=project_item[4])
        project = project_repo.create_project(project_data)


    project_component_seed = [
        ["OVC Funds ACCESS Project Year One", "OVC ACCESS Project Year One", 1], ["OVC ACCESS Project Year Two", "OVC ACCESS Project Year Two", 2],
        ["Technical Fund ACCESS Project Year One", "Technical Fund ACCESS Project Year One", 1], ["Technical ACCESS Project Year One", "Technical ACCESS Project Year Two", 2],
        ["HI Accessories Fund ACCESS Project Year One", "HI Accessories Fund ACCESS Project Year One", 1], ["HI Accessories Fund ACCESS Project Year One", "HI Accessories Fund ACCESS Project Year Two", 2],
        ["Supply Chain Fund ACCESS Project Year One", "Supply Chain Fund ACCESS Project Year One", 1], ["Supply Chain Fund ACCESS Project Year One", "Supply Chain Fund ACCESS Project Year Two", 2]
    ]
    for project_compenent_item in project_component_seed:
        project_compenent_data = ProjectComponentCreate(name=project_compenent_item[0], description=project_compenent_item[1], project_id=project_compenent_item[2])
        project_compoenent = project_component_repo.create_project_component(project_compenent_data)


    funders_seed = [
        ["CDC", "Centre for Disease Control"], ["Global Fund", "Global Fund Grant"], ["Clinton Global Initiatives", "Clinton Global Initiatives"], 
        ["PEPFAR", "US President Emergency Plan For AIDS Relief"]
    ]
    for funders_item in funders_seed:
        funders_data = FunderCreate(name=funders_item[0], description=funders_item[1])
        funders = funders_repo.create_funder(funders_data)


    funding_seed = [
        [1, 1, 1, 1000000], [1, 1, 3, 1000000], [1, 1, 5, 1000000], [1, 1, 7, 400000], 
        [2, 1, 2, 1000000], [2, 1, 4, 1000000], [2, 1, 6, 1000000], [2, 1, 8, 400000]
    ]
    for funding_item in funding_seed:
        funding_data = FundingCreate(project_id=funding_item[0], funder_id=funding_item[1], component_id=funding_item[2], amount_funded=funding_item[3])
        funders = funding_repo.create_funding(funding_data)


    # # Seed Tenancy
    tenancy_seed = ["Abia", "Enugu", "Imo", "Abuja"]
    for tenancy_item in tenancy_seed:
        tenancy_data = TenancyCreate(name=tenancy_item)
        tenancy = tenancy_repo.create_tenancy(tenancy_data)


    # Seed trip_special_location
    trip_special_location_seed = [
        ["Caritas Nigeria State Office", "Abia Caritas State Office", 5.205992, 7.498139, 1],
        ["Caritas Nigeria State Office", "Enugu Caritas State Office", 4.950491, 7.260534, 2],
        ["Caritas Nigeria State Office", "Imo Caritas State Office", 8.953718, 7.467343, 3],
        ["Caritas Nigeria Headquaters Office", "Abuja Caritas Headquaters Office", 5.5408851, 7.456791, 4],
        ["Panyu Hotel and Suites, Aba", "Panyu Hotel and Suites, Aba", 5.385639, 7.433195, 1],
        ["Andy Silk Kingdom College Hotel, Ohafia", "Andy Silk Kingdom College Hotel, Ohafia", 5.107571, 7.362236, 1],
        ["Ibom Water Falls Hotel and Suites, Arochukwu", "Ibom Water Falls Hotel and Suites, Arochukwu", 5.705329, 7.735302, 1],
        ["Sylvia Hotel and Suites, Enugu", "Sylvia Hotel and Suites, Enugu", 5.140383, 7.524912, 2],
        ["Fidelma Hotel and Suites, Enugu", "Fidelma Hotel and Suites, Enugu", 5.51061, 7.52732, 2],
        ["All Seasons Hotel and Suites Owerri", "All Seasons Hotel and Suites, Owerri", 5.385750, 7.433267, 3],
        ["Oxygen Hotel and Suites Owerri", "Oxygen Hotel and Suites, Owerri", 5.107465, 7.362095, 3],
        ["Caritas Nigeria Resource Center, Abuja", "Caritas Nigeria Resource Center, Abuja", 5.617515, 7.849294, 4],
    ]
    for trip_special_location_item in trip_special_location_seed:
        trip_special_location_data = TripStartLocationCreate(name=trip_special_location_item[0], description=trip_special_location_item[1],
                                                             latitude=trip_special_location_item[2], longitude=trip_special_location_item[3], 
                                                             tenancy_id=trip_special_location_item[4])
        trip_special_location = trip_special_location_repo.create_trip_special_location(**trip_special_location_data.model_dump())


    # # Seed Document Type
    document_type_seed = [
        ["O Level Certificate", "O Level Certificate"], ["First Degree Certificate", "First Degree Certificate"],
        ["Post Graduate Certificate", "Post Graduate Certificate"], ["Other Certifications", "Other Certifications"]
    ]
    for document_type_item in document_type_seed:
        document_type_data = DocumentTypeCreate(name=document_type_item[0], description=document_type_item[1])
        document_type = document_type_repo.create_document_type(name=document_type_data.name, description=document_type_data.description)


    # Seed ActionPointSource
    action_point_source_seed = ["SRM Meeting", "Unit Meeting", "Department Meeting", "Review Meeting", "Plenanry Meeting", "General Staff Meeting", "Partner Meeting"]
    for action_point_item in action_point_source_seed:
        action_point_source = ActionPointSourceCreate(name=action_point_item)
        source_action = action_point_source_repo.create_actionpointsource(action_point_source)


    # Seed Issue Status
    issue_status_seed = ["PENDING", "COMPLETED"]
    for issue_status_item in issue_status_seed:
        issue_status_data = IssueStatusCreate(status=issue_status_item)
        status_issue = issue_status_repo.create_issue_status(issue_status_data)


    # Seed IssueLogSource
    issue_log_source_seed = ["Workplan", "Meeting"]
    for issue_log_source_item in issue_log_source_seed:
        issue_log_source_data = IssueLogSourceCreate(name=issue_log_source_item)
        status_issue = issue_log_source_repo.create_issuelogsource(issue_log_source_data)


    # Seed MaintenanceType
    maintenance_type_seed = ["Engine Oil Change", "Pumping of Vehicle Tire", "Sterring Oil Chnage", "Renewal of Vehicle Licence", "Air Condition repair"]
    for maintenance_type_item in maintenance_type_seed:
        maintenance_seed_data = MaintenanceCreate(name=maintenance_type_item)
        maintenance_type = maintenance_type_repo.create_maintenancetype(maintenance_seed_data)


    # Seed Task Status
    task_status_seed = ["PENDING", "COMPLETED"]
    for task_status_item in task_status_seed:
        task_status_data = TaskStatusCreate(name=task_status_item)
        status_task= task_status_repo.create_task_status(task_status_data)


    # Seed Company
    # company_names = ["Caritas Adhoc Staff", "NACA", "SACA", "LACA", "Facility Staff", "Ministry of Health" ]
    # for roles in company_names:
    #     names = Company(name=roles)
    #     db_session.add(names)
    #     db_session.commit()


    # Seed Company
    company_names_seed = [
        ["Caritas Adhoc Staff Abia", 1], ["NACA Abia", 1], ["SACA Abia", 1], ["LACA Abia", 1], ["Facility Staff Abia", 1], ["Ministry of Health, Abia", 1],
        ["Caritas Adhoc Staff Enugu", 2], ["NACA Enugu", 2], ["SACA Enugu", 2], ["LACA Enugu", 2], ["Facility Staff Enugu", 2], ["Ministry of Health, Enugu", 2],
        ["Caritas Adhoc Staff Imo", 3], ["NACA Imo", 3], ["SACA Imo", 3], ["LACA Imo", 3], ["Facility Staff Imo", 3], ["Ministry of Health, Imo", 3]
                        ]
    for company_names_item in company_names_seed:
        comapany_names = CompanyCreate(name=company_names_item[0], tenancy_id=company_names_item[1])
        company = company_repo.create_company(comapany_names)


    # Seed MEAL
    meal_dictionary = {
        1 : "Joll of Rice",
        2 : "Fried Rice",
        3 : "Chineese Rice",
        4 : "Vegetable Soup",
        5 : "Egbusi Soup",
        6 : "Bitter Leaf Soup",
        7 : "Okro Soup",
        8 : "Afang Soup",
        9 : "Chicken",
        10 : "Goat Meat",
        11 : "Beef",
        12 : "Fish",
        13 : "Semo",
        14 : "Garri",
        15 : "Fufu"
    }


    
    meal_combination_seed = [(1, 9), (2, 9), (3, 9), (1, 10), (2, 10), (3, 10), (1, 11), (2, 11), (3, 11), (1, 12), (2, 12), (3, 12),
                             (4, 13, 9), (4, 13, 10), (4, 13, 11), (4, 13, 12), (4, 14, 9), (4, 14, 10), (4, 14, 11), (4, 14, 12),
                             (4, 15, 9), (4, 15, 10), (4, 15, 11), (4, 15, 12), (5, 13, 9), (5, 13, 10), (5, 13, 11), (5, 13, 12),
                             (5, 14, 9), (5, 14, 10), (5, 14, 11), (5, 14, 12), (5, 15, 9), (5, 15, 10), (5, 15, 11), (5, 15, 12),
                             (6, 13, 9), (6, 13, 10), (6, 13, 11), (6, 13, 12), (6, 14, 9), (6, 14, 10), (6, 14, 11), (6, 14, 12),
                             (6, 15, 9), (6, 15, 10), (6, 15, 11), (6, 15, 12), (7, 13, 9), (7, 13, 10), (7, 13, 11), (7, 13, 12),
                             (7, 14, 9), (7, 14, 10), (7, 14, 11), (7, 14, 12), (7, 15, 9), (7, 15, 10), (7, 15, 11), (7, 15, 12),
                             (8, 13, 9), (8, 13, 10), (8, 13, 11), (8, 13, 12), (8, 14, 9), (8, 14, 10), (8, 14, 11), (8, 14, 12),
                             (8, 15, 9), (8, 15, 10), (8, 15, 11), (8, 15, 12)]
    
    
    def get_meal(combo: tuple):
        meals = [meal_dictionary.get(key) for key in combo]
        seed_meal = ', '.join(meals[:-1]) + ' and ' + meals[-1]
        return seed_meal


    for meal_combination_item in meal_combination_seed:
        meals_names = MealCombinationCreate(name=get_meal(meal_combination_item), description=get_meal(meal_combination_item))
        meal = meal_combination_repo.create_meal_combination(name=meals_names.name, description=meals_names.description)



    meeting_type = ["SRM Meeting", "Unit Meeting", "Department Meeting", "Review Meeting", "Plenanry Meeting", "General Staff Meeting", "Partner Meeting"]
    for meeting_type_item in meeting_type:
        types_meeting = MeetingTypeCreate(name=meeting_type_item)
        meeting_type = meeting_type_repo.create_meeting_type(meeting_type=types_meeting)


    # Thematic Area
    thematic_area_seed = ["PBS Optimization", "Viral Load Optimization", "AHD Optimization", "IIT Optimization"]
    for thematic_area_item in thematic_area_seed:
        thematic_area_data = ThematicAreaCreate(name=thematic_area_item)
        thematic_area = thematic_area_repo.create_thematic_area(thematic_area_data)
        

    # Seed Department
    department_seed = [
        "Strategic Information",
        "Admin",
        "Programs",
        "Care and Treatment",
        "Finance",
        "Pharmacy",
        "Laboratory",
        "Ophans and Vulnerable",
        "Prevention",
        "Communication",
    ]
    for departement_item in department_seed:
        department_data = DepartmentCreate(name=departement_item)
        department = department_repo.create_department(department_data)

    # Seed Unit
    unit_seed = [
        ["Health Informatics Unit", 1],
        ["Quality Improvement and Surveillance Unit", 1],
        ["Monitoring and Evaluation Unit", 1],
        ["Admin Unit", 2],
        ["Procurement Unit", 2],
        ["ICT_unit", 2],
        ["Transport and logistics Unit", 2],
        ["Program Unit", 3],
        ["Care and Treatment Unit", 4],
        ["Grant Unit", 5],
        ["Finance Unit", 5],
        ["Pharmacy Unit", 6],
        ["LaboratoryUnit", 7],
        ["Ophans and Vulnerable Unit", 8],
        ["Prevention Unit", 9],
        ["Communication", 10],
    ]
    for unit_item in unit_seed:
        unit_data = UnitCreate(name=unit_item[0], department_id=unit_item[1])
        unit = unit_repo.create_unit(unit_data)

    # Seed SRT
    srt_seed = [
        ["SRT A", "Abia SRT A",1],
        ["SRT B", "Abia SRT B",1],
        ["SRT C", "Abia SRT C",1],
        ["SRT D", "Abia SRT D",1],
        ["SRT A", "Enugu SRT A",2],
        ["SRT B", "Enugu SRT B",2],
        ["SRT C", "Enugu SRT C",2],
        ["SRT D", "Enugu SRT D",2],
        ["SRT A", "Imo SRT A", 3],
        ["SRT B", "Imo SRT B", 3],
        ["SRT C", "Imo SRT C", 3],
        ["SRT D", "Imo SRT D", 3],
    ]
    for srt_item in srt_seed:
        srt_data = SRTCreate(name=srt_item[0], description=srt_item[1], tenancy_id=srt_item[2])
        srt = srt_repo.create_srt(srt_data)

    # Seed Designation
    designation_seed = [
        "Executive Secretary/CEO",
        "Deputy Executive Secretary",
        "Chief of Party",
        "Program Director",
        "Director",
        "Associate Director",
        "Senior Advisor",
        "Advisor",
        "Senior Specialist/Senior Program Manager",
        "Specialist/Program Manager",
        "Senior Officer",
        "Officer",
        "Associate",
        "Assistant",
    ]
    for designation_item in designation_seed:
        designation_data = DesignationCreate(name=designation_item)
        designation = designation_repo.create_designation(designation_data)

    # Seed Employee
    for employee_item in employee_seed:
        employee_data = EmployeeCreate(
            first_name=employee_item[0],
            last_name=employee_item[1],
            phone_number="+234" + employee_item[2],
            department_id=employee_item[3],
            unit_id=employee_item[4],
            staff_code=employee_item[5],
            employee_email=employee_item[6],
            address=employee_item[7],
            state_origin=employee_item[8],
            lga_origin=employee_item[9],
            date_of_birth=datetime.strptime(employee_item[10], "%d/%m/%Y"),
            designation_id=employee_item[11],
            tenancy_id=employee_item[12],
            gender=employee_item[15],
        )
        employee = employee_repo.create_employee(employee_data)

    # Seed UserRole
    user_roles_seed = [
        "super_admin",
        "hr",
        "tenant_admin",
        "stl",
        "technical_lead",
        "programs_lead",
        "program_team",
        "admin_team",
        "admin_lead",
        "unit_lead",
        "department_lead",
        "unit_member",
        "hq_backstop",
        "driver",
        "chief_driver",
    ]
    for user_roles_item in user_roles_seed:
        user_role_data = UserRoleCreate(name=user_roles_item)
        role = user_role_repo.create_role(user_role_data)

    # Seed Location
    location_seed = [
        ["Aba", 1],
        ["Arochukwu", 1],
        ["Ohafia", 1],
        ["Umuahia", 1],
        ["Owerri Municipal", 3],
        ["Owerri North", 3],
        ["Orlu", 3],
        ["Okigwe", 3],
        ["Ngor Okpala", 3],
        ["Obowo", 3],
        ["Awgu", 2],
        ["Nsukka", 2],
        ["Enugu North", 2],
        ["Enugu East", 2],
        ["Udi", 2]
    ]
    for location in location_seed:
        location_data = LocationCreate(name=location[0], tenancy_id=int(location[1]))
        locations = location_repo.create_location(location_data=location_data)

    # Seed WorkPlanSource
    workplan_source_seed = [
        "Unit",
        "Department",
        "SRT",
        "ThematicArea",
        "Special Assignments",
    ]
    for source in workplan_source_seed:
        workplan_source_data = WorkPlanSourceCreate(name=source)
        workplan_source = workplan_source_repo.create_work_plan_source(
            work_plan_type_data=workplan_source_data
        )

    # Seed Sites
    sites_seed = [
        ["Abia State Specialist Hospital, Amachara", "Facility", 1, 4],
        ["Federal Medical Centre Umuahia", "Facility", 1, 4],
        ["New Era", "Facility", 1, 1],
        ["Mendel", "Facility", 1, 1],
        ["St Anthony Arochukwu", "Facility", 1, 2],
        ["General Hospital Arochukwu", "Facility", 1, 2],
        ["General Hospital Ohafia", "Facility", 1, 3],
        ["King of kings Ohafia", "Facility", 1, 3],
        ["Okigwe General Hospital", "Facility", 3, 8],
        ["Federal Medical Centre Owerri", "Facility", 3, 5],
        ["Imo State University Teaching Hospital", "Facility", 3, 7],
        ["St Damian Catholic Hospital", "Facility", 3, 7],
        ["Imo State Specialist Hospital", "Facility", 3, 5],
        ["Holy Rosary Hospital Emekuku", "Facility", 3, 6],
        ["Ngor Okpala General Hospital", "Facility", 3, 9],
        ["Our Lady of Mercy, Obowo", "Facility", 3, 10],
        ["Mother of Christ Specialist Hospital", "Facility", 2, 13],
        ["Enugu State Teaching Hospital", "Facility", 2, 13],
        ["Agwu General Hospital", "Facility", 2, 11],
        ["Agwu Health Centre", "Facility", 2, 11],
        ["Nsukka General Hospital", "Facility", 2, 12],
        ["Bishop Shanahan Hospital", "Facility", 2, 12],
        ["Faith Foundation Hospital", "Facility", 2, 12],
        ["Annunciation Specialist Hospital", "Facility", 2, 12],
        ["Udi General Hospital", "Facility", 2, 15]
    ]
    for sites in sites_seed:
        sites_data = SiteCreate(
            name=sites[0], site_type=sites[1], tenancy_id=sites[2], location_id=sites[3]
        )
        sites_create = sites_repo.create_site(site_data=sites_data)

    # Seed User
    employee_no = 1
    for user_item in employee_seed:
        hashed_password = "Admin123"
        user_data = UserCreate(
            username=user_item[0],
            email=user_item[6],
            password=hashed_password,
            employee_id=employee_no,
            tenancy_id=user_item[12],
        )
        user = user_repo.create_user(db_session, user_data)
        employee_no += 1


    # Meeting
    meeting_seed = [["SRM week 1", datetime.now(), datetime.now() + timedelta(hours=3), 2, 37, "VIRTUAL", False, False], ["SRM week 2", datetime.now(), datetime.now() + timedelta(hours=3), 1, 1, "VIRTUAL", False, False],
                    ["HI Meeting", datetime.now(), datetime.now() + timedelta(hours=3), 1, 1, "PHYSICAL", True, False]]
    for meeting_item in meeting_seed:
        meeting_data = MeetingCreate(name=meeting_item[0], date_start=meeting_item[1],date_end=meeting_item[2], meeting_type_id=meeting_item[3], organizer_id=meeting_item[4], 
                                     meeting_category=meeting_item[5], is_meal_required=meeting_item[6], is_third_party_required=meeting_item[7])
        meeting = meeting_repo.create_meeting(**meeting_data.dict())


    # User Roles
    user_no = 1
    for users_role_item in employee_seed:
        roles_items = (users_role_item[14]).split(sep=", ")
        user_role = RoleAssignment(user_id=user_no, roles=roles_items)
        asign_roles = user_repo.assign_roles(
            user_id=user_role.user_id, role_ids=user_role.roles
        )
        user_no += 1


    ## Seed Drivers
    drivers_data = [
        [51, "ABI00000001", "2025-02-01", 1, True],
        [52, "ABI00000002", "2024-12-12", 1, True],
        [53, "ABI00000003", "2024-12-05", 1, True],
        [54, "ABI00000004", "2025-01-25", 1, True],
        [55, "ABI00000005", "2025-01-25", 1, True],
        [56, "ABI00000006", "2025-01-25", 1, True],
        [57, "ABI00000007", "2025-01-25", 1, True],
        [58, "ABI00000008", "2025-01-25", 1, True],
        [59, "ABI00000009", "2025-01-25", 1, True],
        [60, "ABI00000010", "2025-01-25", 1, True],
        [61, "ABI00000011", "2025-01-25", 1, True],
        [62, "ABI00000012", "2025-01-25", 1, True],
        [105, "ABI00000013", "2025-01-25", 3, True],
        [106, "ABI00000014", "2025-01-25", 3, True],
        [107, "ABI00000015", "2025-01-25", 3, True],
        [108, "ABI00000016", "2025-01-25", 3, True],
        [109, "ABI00000017", "2025-01-25", 3, True],
        [110, "ABI00000018", "2025-01-25", 3, True],
        [111, "ABI00000019", "2025-01-25", 3, True],
        [112, "ABI00000020", "2025-01-25", 3, True],
        [113, "ABI00000021", "2025-01-25", 3, True],
        [114, "ABI00000022", "2025-01-25", 3, True],
        [163, "ABI00000023", "2025-01-25", 2, True],
        [179, "ABI00000024", "2025-01-25", 2, True],
        [189, "ABI00000025", "2025-01-25", 2, True],
        [194, "ABI00000026", "2025-01-25", 2, True],
        [199, "ABI00000027", "2025-01-25", 2, True],
        [200, "ABI00000028", "2025-01-25", 2, True],
        [201, "ABI00000029", "2025-01-25", 2, True],
        [203, "ABI00000030", "2025-01-25", 2, True],
        [209, "ABI00000031", "2025-01-25", 2, True],

    ]
    for driver in drivers_data:
        driver_info = DriverCreate(
            user_id=driver[0],
            licence_number=driver[1],
            licence_exp_date=driver[2],
            tenancy_id=driver[3],
            is_available=driver[4],
        )
        drivers_create = driver_repo.create_driver(driver_data=driver_info)

    ## Seed Vehicles
    vehicles_data = [
        ["White Bus", "32J321FG", "ABU101", "Toyota", 2018, "Petrol", 270, 6, 16, 1],
        ["4Runner Jeep", "12R890FG", "ABU102", "Toyota", 2017, "Petrol", 280, 7, 4, 1],
        ["4Runner Jeep", "32J211FG", "ABU103", "Toyota", 2016, "Petrol", 280, 7, 4, 1],
        ["White Bus", "12R933FG", "ABU104", "Toyota", 2019, "Petrol", 270, 6, 16, 1],
        ["4Runner Jeep", "32J111FG", "ABU105", "Toyota", 2019, "Petrol", 280, 7, 4, 1],
        ["Prado Jeep", "32J318FG", "ABI106", "Toyota", 2019, "Petrol", 285, 8, 6, 1],
        ["White Bus", "32J321EN", "ABU106", "Toyota", 2018, "Petrol", 270, 6, 16, 2],
        ["4Runner Jeep", "12R890EN", "ABU107", "Toyota", 2017, "Petrol", 280, 7, 4, 2],
        ["4Runner Jeep", "32J211EN", "ABU108", "Toyota", 2016, "Petrol", 280, 7, 4, 2],
        ["White Bus", "12R933EN", "ABU109", "Toyota", 2019, "Petrol", 270, 6, 16, 2],
        ["4Runner Jeep", "32J111EN", "ABU110", "Toyota", 2019, "Petrol", 280, 7, 4, 2],
        ["Prado Jeep", "32J318EN", "ABI111", "Toyota", 2019, "Petrol", 285, 8, 6, 2],
        ["White Bus", "32J321IM", "ABU112", "Toyota", 2018, "Petrol", 270, 6, 16, 3],
        ["4Runner Jeep", "12R890IM", "ABU113", "Toyota", 2017, "Petrol", 280, 7, 4, 3],
        ["4Runner Jeep", "32J211IM", "ABU114", "Toyota", 2016, "Petrol", 280, 7, 4, 3],
        ["White Bus", "12R933IM", "ABU115", "Toyota", 2019, "Petrol", 270, 6, 16, 3],
        ["4Runner Jeep", "32J111IM", "ABU116", "Toyota", 2019, "Petrol", 280, 7, 4, 3],
        ["Prado Jeep", "32J318IM", "ABI117", "Toyota", 2019, "Petrol", 285, 8, 6, 3],
    ]
    for vehicles in vehicles_data:
        vehicle_info = VehicleCreate(
            name=vehicles[0],
            licence_plate=vehicles[1],
            alternate_plate=vehicles[2],
            make=vehicles[3],
            year=vehicles[4],
            fuel_type=vehicles[5],
            current_mileage=vehicles[6],
            fuel_economy=vehicles[7],
            seat_capacity=vehicles[8],
            tenancy_id=vehicles[9],
        )
        vehicle_create = vehicle_repo.create_vehicle(vehicle_info=vehicle_info)

    print(f"Seeded Tenancy: {tenancy.name}")
    print(f"Seeded Department: {department.name}")
    print(f"Seeded Unit: {unit.name}")
    print(f"Seeded SRT: {srt.name}")
    print(f"Seeded Employee: {employee.first_name} {employee.last_name}")
    print(f"Seeded Designation: {designation.name}")
    print(f"Seeded UserRole: {role.name}")
    print(f"Seeded User: {user.username}")
    print(f"Seeded User Roles {user.roles}")
    print(f"Seeded Location {locations.name}")
    print(f"Seeded WorkPlanSource {workplan_source.name}")
    print(f"Seeded Sites {sites_create.name}")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def main():
    db_session = SessionLocal()

    try:
        csv_file = "staff_directory.csv"
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
