# # from sqlalchemy import (
# #     Column, Float, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Text, Date, Table, Enum, Time
# # )
# # from sqlalchemy.orm import relationship, declarative_base
# # import datetime
# # from db.database import Base

# # class Employee(Base):
# #     __tablename__ = 'employees'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     first_name = Column(String(50), nullable=False)
# #     last_name = Column(String(50), nullable=False)
# #     email = Column(String(100), unique=True, nullable=False)
# #     phone_number = Column(String(20), unique=True, nullable=False)
# #     address = Column(String(255))
# #     date_of_birth = Column(Date)
# #     date_of_hire = Column(Date, nullable=False)
# #     job_position_id = Column(Integer, ForeignKey('job_positions.id'))
# #     department_id = Column(Integer, ForeignKey('departments.id'))
# #     supervisor_id = Column(Integer, ForeignKey('employees.id'))
# #     emergency_contact = Column(String(100))
# #     emergency_contact_phone = Column(String(20))
# #     employment_status = Column(String(50), nullable=False)  # e.g., Active, Inactive, Terminated
# #     salary = Column(Float, nullable=False)
# #     is_active = Column(Boolean, default=True)

# #     job_position = relationship('JobPosition', back_populates='employees')
# #     department = relationship('Department', back_populates='employees')
# #     supervisor = relationship('Employee', remote_side=[id])
# #     leaves = relationship('Leave', back_populates='employee')
# #     attendance_records = relationship('Attendance', back_populates='employee')
# #     performance_reviews = relationship('PerformanceReview', back_populates='employee')
# #     trainings = relationship('Training', secondary='employee_training', back_populates='employees')


# # class JobPosition(Base):
# #     __tablename__ = 'job_positions'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     title = Column(String(100), nullable=False)
# #     description = Column(Text)
# #     department_id = Column(Integer, ForeignKey('departments.id'))

# #     department = relationship('Department', back_populates='job_positions')
# #     employees = relationship('Employee', back_populates='job_position')


# # class Department(Base):
# #     __tablename__ = 'departments'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     name = Column(String(100), nullable=False)
# #     description = Column(Text)

# #     job_positions = relationship('JobPosition', back_populates='department')
# #     employees = relationship('Employee', back_populates='department')


# # class Leave(Base):
# #     __tablename__ = 'leaves'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     employee_id = Column(Integer, ForeignKey('employees.id'))
# #     leave_type = Column(String(50), nullable=False)  # e.g., Annual, Sick, Maternity
# #     start_date = Column(Date, nullable=False)
# #     end_date = Column(Date, nullable=False)
# #     status = Column(String(50), nullable=False)  # e.g., Pending, Approved, Rejected
# #     reason = Column(Text)

# #     employee = relationship('Employee', back_populates='leaves')


# # class Attendance(Base):
# #     __tablename__ = 'attendance'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     employee_id = Column(Integer, ForeignKey('employees.id'))
# #     date = Column(Date, nullable=False)
# #     check_in_time = Column(Time)
# #     check_out_time = Column(Time)
# #     status = Column(String(50), nullable=False)  # e.g., Present, Absent, On Leave, On Trip

# #     employee = relationship('Employee', back_populates='attendance_records')


# # class PerformanceReview(Base):
# #     __tablename__ = 'performance_reviews'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     employee_id = Column(Integer, ForeignKey('employees.id'))
# #     review_date = Column(Date, nullable=False)
# #     reviewer_id = Column(Integer, ForeignKey('employees.id'))
# #     score = Column(Integer, nullable=False)  # e.g., from 1 to 10
# #     comments = Column(Text)

# #     employee = relationship('Employee', back_populates='performance_reviews')
# #     reviewer = relationship('Employee', remote_side=[id])


# # class Training(Base):
# #     __tablename__ = 'trainings'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     title = Column(String(100), nullable=False)
# #     description = Column(Text)
# #     start_date = Column(Date, nullable=False)
# #     end_date = Column(Date, nullable=False)
# #     location = Column(String(255))

# #     employees = relationship('Employee', secondary='employee_training', back_populates='trainings')


# # class EmployeeTraining(Base):
# #     __tablename__ = 'employee_training'
    
# #     employee_id = Column(Integer, ForeignKey('employees.id'), primary_key=True)
# #     training_id = Column(Integer, ForeignKey('trainings.id'), primary_key=True)


# # class Payroll(Base):
# #     __tablename__ = 'payroll'
    
# #     id = Column(Integer, primary_key=True, autoincrement=True)
# #     employee_id = Column(Integer, ForeignKey('employees.id'))
# #     pay_date = Column(Date, nullable=False)
# #     pay_period_start = Column(Date, nullable=False)
# #     pay_period_end = Column(Date, nullable=False)
# #     gross_pay = Column(Float, nullable=False)
# #     net_pay = Column(Float, nullable=False)
# #     deductions = Column(Float, nullable=False)
# #     bonuses = Column(Float, nullable=False)

# #     employee = relationship('Employee')




# from sqlalchemy import (
#     Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Text, Date, Table, Enum as SQLAEnum, Time
# )
# from sqlalchemy.orm import relationship, declarative_base, configure_mappers
# from enum import Enum as PyEnum
# import datetime
# from db.database import Base

# class BaseTable(Base):
#     __abstract__ = True
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     is_active = Column(Boolean, default=True, comment="Soft delete flag")
#     date_created = Column(DateTime, default=datetime.datetime.utcnow)
#     date_updated = Column(DateTime, onupdate=datetime.datetime.utcnow, nullable=True)
#     date_deleted = Column(DateTime, nullable=True)

# class MeetingCategory(PyEnum):
#     VIRTUAL = "Virtual Meeting"
#     PHYSICAL = "Physical Meeting"

# class ActionEnum(PyEnum):
#     CREATE = "CREATE"
#     READ = "READ"
#     UPDATE = "UPDATE"
#     SOFT_DELETE = "SOFT_DELETE"
#     DELETE = "DELETE"
#     CUSTOM_QUERY = "CUSTOM_QUERY"
#     APPROVE = "APPROVE"
#     DENY = "DENY"
#     SCHEDULE_TRIP = "SCHEDULE_TRIP"
#     RESCHEDULE = "RESCHEDULE"
#     RESTORE = "RESTORE"
#     REVIEW = "REVIEW"
#     START_TRIP = "START_TRIP"
#     END_TRIP = "END_TRIP"
#     TRIP_REPORT_DOWNLOAD = "TRIP_REPORT_DOWNLOAD"  
#     SUBMIT_TRIP_REPORT = "SUBMIT_TRIP_REPORT"  
#     COMPLETED = "COMPLETED"
#     RE_OPENED = "RE_OPENED"

# class MealSelectionType(PyEnum):
#     EMPLOYEE = "Employee"
#     THIRD_PARTY = "Third Party"

# class MeetingParticipantType(PyEnum):
#     EMPLOYEE = "Employee"
#     THIRD_PARTY = "Third Party"

# # Association Tables
# users_roles = Table(
#     'users_roles', Base.metadata,
#     Column('user_id', ForeignKey('users.id'), primary_key=True),
#     Column('role_id', ForeignKey('user_roles.id'), primary_key=True)
# )

# employee_srt_association = Table(
#     'employee_srt', Base.metadata,
#     Column('employee_id', ForeignKey('employees.id'), primary_key=True),
#     Column('srt_id', ForeignKey('srts.id'), primary_key=True)
# )

# workplan_employee_association = Table(
#     'workplan_employee', Base.metadata,
#     Column('work_plan_id', ForeignKey('work_plans.id'), primary_key=True),
#     Column('employee_id', ForeignKey('employees.id'), primary_key=True)
# )

# workplan_site_association = Table(
#     'workplan_site_association', Base.metadata,
#     Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True),
#     Column('site_id', Integer, ForeignKey('sites.id'), primary_key=True)
# )

# trip_workplan_association = Table(
#     'trip_workplan_association', Base.metadata,
#     Column('trip_id', Integer, ForeignKey('trips.id'), primary_key=True),
#     Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True)
# )

# workplan_location_association = Table(
#     'workplan_location_association', Base.metadata,
#     Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True),
#     Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True)
# )

# focal_person_issue_association = Table(
#     'focal_person_issue_association', Base.metadata,
#     Column('issue_logs_id', Integer, ForeignKey('issue_logs.id'), primary_key=True),
#     Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
# )

# task_employee_association = Table(
#     'task_employee_association', Base.metadata,
#     Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
#     Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
# )

# assignment_tenancy_association = Table(
#     'assignment_tenancy_association', Base.metadata,
#     Column('assignment_id', Integer, ForeignKey('assignments.id'), primary_key=True),
#     Column('tenancy_id', Integer, ForeignKey('tenancy.id'), primary_key=True)
# )

# assignment_employee_association = Table(
#     'assignment_employee_association', Base.metadata,
#     Column('assignment_id', Integer, ForeignKey('assignments.id'), primary_key=True),
#     Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
# )

# meeting_employee_association = Table(
#     'meeting_employee_association', Base.metadata,
#     Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
#     Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
# )

# meeting_thirdparty_association = Table(
#     'meeting_thirdparty_association', Base.metadata,
#     Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
#     Column('thirdparty_id', Integer, ForeignKey('third_party_participants.id'), primary_key=True)
# )

# project_tenancy_association = Table(
#     'project_tenancy_association', Base.metadata,
#     Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
#     Column('tenancy_id', Integer, ForeignKey('tenancy.id'), primary_key=True)
# )

# project_employee_association = Table(
#     'project_employee_association', Base.metadata,
#     Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
#     Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
# )

# # User and Role Models
# class UserRole(BaseTable):
#     __tablename__ = 'user_roles'
#     name = Column(String(50), unique=True, nullable=False)
#     users = relationship("User", secondary=users_roles, back_populates="roles")

# class User(BaseTable):
#     __tablename__ = 'users'
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#     hashed_password = Column(Text, nullable=False)
#     reset_token = Column(String(100), nullable=True)
#     reset_token_expires = Column(DateTime, nullable=True)
#     employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True, unique=True)
#     roles = relationship("UserRole", secondary=users_roles, back_populates="users")
#     employee = relationship("Employee", back_populates="user", uselist=False)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="users")
#     driver = relationship("Driver", back_populates="user", uselist=False)
#     audit_logs = relationship("AuditLog", back_populates="user")
#     login_history = relationship("LoginHistory", back_populates="user")
#     assignments = relationship("Assignment", back_populates="initiating_user")

# class LoginHistory(BaseTable):
#     __tablename__ = 'login_history'
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     login_time = Column(DateTime, default=datetime.datetime.utcnow)
#     logout_time = Column(DateTime, nullable=True)
#     ip_address = Column(String(45), nullable=True)
#     user_agent = Column(String(255), nullable=True)
#     user = relationship("User", back_populates="login_history")

# class InvalidToken(BaseTable):
#     __tablename__ = 'invalid_tokens'
#     token = Column(String, nullable=False, unique=True)
#     expiry_date = Column(DateTime, nullable=False)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship("User")

# class Setting(BaseTable):
#     __tablename__ = 'settings'
#     setting_name = Column(String(100), nullable=False, unique=True)
#     value = Column(Text, nullable=False)

# # Tenancy and Organization Models
# class Tenancy(BaseTable):
#     __tablename__ = 'tenancy'
#     name = Column(String(255), unique=True)
#     locations = relationship("Location", back_populates="tenancy")
#     sites = relationship("Site", back_populates="tenancy")
#     srts = relationship("SRT", back_populates="tenancy")
#     employees = relationship("Employee", back_populates="tenancy")
#     vehicles = relationship("Vehicle", back_populates="tenancy")
#     drivers = relationship("Driver", back_populates="tenancy")
#     trips = relationship("Trip", back_populates="tenancy")
#     trip_reports = relationship("TripReport", back_populates="tenancy")
#     fuel_purchases = relationship("FuelPurchase", back_populates="tenancy")
#     vehicle_maintenances = relationship("VehicleMaintenance", back_populates="tenancy")
#     users = relationship("User", back_populates="tenancy")
#     work_plans = relationship("WorkPlan", back_populates="tenancy")
#     assignments = relationship("Assignment", secondary=assignment_tenancy_association, back_populates="tenancies")
#     issues = relationship("IssueLog", back_populates="tenancy")
#     projects = relationship("Project", secondary=project_tenancy_association, back_populates="tenancies")

# class Department(BaseTable):
#     __tablename__ = 'departments'
#     name = Column(String(255), unique=True, nullable=False)
#     employees = relationship("Employee", back_populates="department")
#     units = relationship("Unit", back_populates="department")
#     issues = relationship("IssueLog", back_populates="department")

# class Unit(BaseTable):
#     __tablename__ = 'units'
#     name = Column(String(100), unique=True, nullable=False)
#     department_id = Column(Integer, ForeignKey('departments.id'))
#     employees = relationship("Employee", back_populates="unit")
#     department = relationship("Department", back_populates="units")
#     issues = relationship("IssueLog", back_populates="unit")

# class Employee(BaseTable):
#     __tablename__ = 'employees'
#     first_name = Column(String(255), nullable=False)
#     last_name = Column(String(255), nullable=False)
#     phone_number = Column(String(25), unique=True, nullable=False)
#     staff_code = Column(String(100), unique=True, nullable=False)
#     employee_email = Column(String(100), unique=True, nullable=False)
#     address = Column(Text, nullable=True)
#     state_origin = Column(String(100), nullable=False)
#     lga_origin = Column(String(100), nullable=False)
#     date_of_birth = Column(Date, nullable=True)
#     gender = Column(String(20), nullable=True)
#     designation_id = Column(Integer, ForeignKey('designations.id'), nullable=True)
#     department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
#     unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'), nullable=False)
#     signature = Column(Text, nullable=True)
#     tenancy = relationship("Tenancy", back_populates="employees")
#     designation = relationship("Designation", back_populates="employees")
#     department = relationship("Department", back_populates="employees")
#     unit = relationship("Unit", back_populates="employees")
#     srts = relationship("SRT", secondary=employee_srt_association, back_populates="employees")
#     user = relationship("User", back_populates="employee", uselist=False)
#     led_work_plans = relationship("WorkPlan", back_populates="activity_lead")
#     work_plans = relationship("WorkPlan", secondary=workplan_employee_association, back_populates="employees")
#     issue_logs_reported = relationship("IssueLog", foreign_keys="IssueLog.reported_by_id")
#     organized_meetings = relationship("Meeting", back_populates="organizer")
#     assigned_action_points = relationship("ActionPoint", back_populates="responsible")
#     tasks = relationship("Task", secondary=task_employee_association, back_populates="employees")
#     led_assignments = relationship("Assignment", back_populates="assignment_lead")
#     assignments = relationship("Assignment", secondary=assignment_employee_association, back_populates="responsible_employees")
#     issues = relationship("IssueLog", secondary=focal_person_issue_association, back_populates="employees")
#     milestones = relationship("Milestone", back_populates="responsible_employee")
#     meetings = relationship("Meeting", secondary=meeting_employee_association, back_populates="attendees")
#     meal_selections = relationship("MealSelection", back_populates="employee", cascade="all, delete-orphan")
#     meeting_participations = relationship("MeetingParticipant", back_populates="employee")
#     projects = relationship("Project", secondary=project_employee_association, back_populates="employees")

# class Designation(BaseTable):
#     __tablename__ = 'designations'
#     name = Column(String(100), unique=True)
#     employees = relationship("Employee", back_populates="designation")

# class SRT(BaseTable):
#     __tablename__ = 'srts'
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="srts")
#     employees = relationship("Employee", secondary=employee_srt_association, back_populates="srts")
#     issues = relationship("IssueLog", back_populates="srt")

# class Location(BaseTable):
#     __tablename__ = 'locations'
#     name = Column(String(255))
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="locations")
#     sites = relationship("Site", back_populates="location")
#     work_plans = relationship("WorkPlan", secondary=workplan_location_association, back_populates="locations")

# class Site(BaseTable):
#     __tablename__ = 'sites'
#     name = Column(String(255), nullable=False)
#     site_type = Column(String(100), nullable=False)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     location_id = Column(Integer, ForeignKey('locations.id'))
#     tenancy = relationship("Tenancy", back_populates="sites")
#     location = relationship("Location", back_populates="sites")
#     issues = relationship("IssueLog", back_populates="site")
#     work_plans = relationship("WorkPlan", secondary=workplan_site_association, back_populates="sites")
#     third_party_participants = relationship("ThirdPartyParticipant", back_populates="site")

# class ThematicArea(BaseTable):
#     __tablename__ = 'thematic_areas'
#     name = Column(String(255), nullable=False, unique=True)
#     issues = relationship("IssueLog", back_populates="thematic_area")
#     workplans = relationship("WorkPlan", back_populates="thematic_area")

# # WorkPlan and Assignment Models
# class WorkPlan(BaseTable):
#     __tablename__ = 'work_plans'
#     workplan_code = Column(String(20), nullable=True)
#     activity_title = Column(String(255), nullable=False)
#     specific_task = Column(Text, nullable=False)
#     logistics_required = Column(String(100), nullable=True) 
#     reason = Column(Text, nullable=True)
#     status = Column(String(20), nullable=True)
#     activity_start_time = Column(Time, nullable=True)
#     activity_date = Column(Date, nullable=False)
#     date_reviewed = Column(DateTime, nullable=True)
#     date_approved = Column(DateTime, nullable=True)
#     date_rescheduled = Column(DateTime, nullable=True)
#     date_denied = Column(DateTime, nullable=True)
#     is_rescheduled = Column(Boolean, default=False, nullable=False)
#     is_denied = Column(Boolean, default=False, nullable=False)
#     is_approved = Column(Boolean, default=False, nullable=False)
#     archived = Column(Boolean, default=False, nullable=False)
#     is_report_submitted = Column(Boolean, default=False, nullable=True)
#     need_vehicle = Column(Boolean, default=False, nullable=True)
#     vehicle_assigned = Column(Boolean, default=False, nullable=True)
#     initiating_user_id = Column(Integer, ForeignKey('users.id'))
#     initiating_unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
#     reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
#     approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
#     initiating_srt_id = Column(Integer, ForeignKey('srts.id'), nullable=True)
#     initiating_department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
#     initiating_thematic_area_id = Column(Integer, ForeignKey('thematic_areas.id'), nullable=True)
#     group_id = Column(Integer, nullable=True)
#     initiating_user = relationship("User", foreign_keys=[initiating_user_id])
#     reviewing_user = relationship("User", foreign_keys=[reviewed_by])
#     approving_user = relationship("User", foreign_keys=[approved_by])
#     initiating_unit = relationship("Unit", foreign_keys=[initiating_unit_id])
#     initiating_srt = relationship("SRT", foreign_keys=[initiating_srt_id])
#     initiating_department = relationship("Department", foreign_keys=[initiating_department_id])
#     thematic_area = relationship("ThematicArea", foreign_keys=[initiating_thematic_area_id])
#     workplan_source_id = Column(Integer, ForeignKey('workplan_sources.id'))
#     workplan_source = relationship("WorkPlanSource", back_populates="workplans")
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="work_plans")
#     activity_lead_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     activity_lead = relationship("Employee", back_populates="led_work_plans")
#     trip_report = relationship("TripReport", back_populates="work_plan", uselist=False)
#     sites = relationship("Site", secondary=workplan_site_association, back_populates="work_plans")
#     employees = relationship("Employee", secondary=workplan_employee_association, back_populates="work_plans")
#     trips = relationship("Trip", secondary=trip_workplan_association, back_populates="work_plans")
#     locations = relationship("Location", secondary=workplan_location_association, back_populates="work_plans")

# class WorkPlanSource(BaseTable):
#     __tablename__ = 'workplan_sources'
#     name = Column(String(100), unique=True)
#     workplans = relationship("WorkPlan", back_populates="workplan_source")

# class Assignment(BaseTable):
#     __tablename__ = 'assignments'
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=True)
#     status = Column(String(50), nullable=False, default="Active")
#     assignment_lead_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     initiating_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     comment = Column(Text, nullable=True)
#     date_completed = Column(Date, nullable=True)
#     is_completed = Column(Boolean, default=False)
#     assignment_lead = relationship("Employee", back_populates="led_assignments")
#     initiating_user = relationship("User", back_populates="assignments")
#     tenancies = relationship("Tenancy", secondary=assignment_tenancy_association, back_populates="assignments")
#     tasks = relationship("Task", back_populates="assignment")
#     responsible_employees = relationship("Employee", secondary=assignment_employee_association, back_populates="assignments")
#     milestones = relationship("Milestone", back_populates="assignment")

# class Task(BaseTable):
#     __tablename__ = 'tasks'
#     description = Column(Text, nullable=False)
#     assignment_id = Column(Integer, ForeignKey('assignments.id'))
#     due_date = Column(Date, nullable=True)
#     date_completed = Column(Date, nullable=True)
#     is_completed = Column(Boolean, default=False)
#     status_id = Column(Integer, ForeignKey('task_statuses.id'), nullable=False)
#     milestone_id = Column(Integer, ForeignKey('milestones.id'), nullable=True)
#     comment = Column(Text, nullable=True)
#     milestone = relationship("Milestone", back_populates="tasks")
#     assignment = relationship("Assignment", back_populates="tasks")
#     status = relationship("TaskStatus", back_populates="tasks")
#     employees = relationship("Employee", secondary=task_employee_association, back_populates="tasks")

# class TaskStatus(BaseTable):
#     __tablename__ = 'task_statuses'
#     name = Column(String(50), nullable=False, unique=True)
#     tasks = relationship("Task", back_populates="status")

# class Milestone(BaseTable):
#     __tablename__ = 'milestones'
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     due_date = Column(Date, nullable=False)
#     completion_date = Column(Date, nullable=True)
#     status = Column(String(50), nullable=False, default="Pending")
#     assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
#     responsible_employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
#     comment = Column(Text, nullable=True)
#     date_completed = Column(Date, nullable=True)
#     is_completed = Column(Boolean, default=False)
#     assignment = relationship("Assignment", back_populates="milestones")
#     responsible_employee = relationship("Employee", back_populates="milestones")
#     tasks = relationship("Task", back_populates="milestone")

# # Meeting Models
# class MeetingType(BaseTable):
#     __tablename__ = 'meeting_types'
#     name = Column(String(255), nullable=False, unique=True)
#     meetings = relationship("Meeting", back_populates="meeting_type")

# class Company(BaseTable):
#     __tablename__ = 'companies'
#     name = Column(String(255), nullable=False, unique=True)
#     third_party_participants = relationship("ThirdPartyParticipant", back_populates="company")

# class ThirdPartyParticipant(BaseTable):
#     __tablename__ = 'third_party_participants'
#     name = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False, unique=True)
#     phone_number = Column(String(50), nullable=True)
#     company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
#     site_id = Column(Integer, ForeignKey('sites.id'), nullable=True)
#     meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=True)
#     meal_selections = relationship("MealSelection", back_populates="third_party_participant", cascade="all, delete-orphan")
#     company = relationship("Company", back_populates="third_party_participants")
#     site = relationship("Site", back_populates="third_party_participants")
#     meeting = relationship("Meeting", back_populates="third_party_participants")
#     meeting_participations = relationship("MeetingParticipant", back_populates="third_party_participant")
#     meetings = relationship("Meeting", secondary=meeting_thirdparty_association, back_populates="third_party_attendees")


# class MealCombination(BaseTable):
#     __tablename__ = 'meal_combinations'
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     meal_selections = relationship("MealSelection", back_populates="meal_combination", cascade="all, delete-orphan")

# class MealSelection(BaseTable):
#     __tablename__ = 'meal_selections'
#     selection_type = Column(SQLAEnum(MealSelectionType), nullable=False)
#     employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     third_party_participant_id = Column(Integer, ForeignKey('third_party_participants.id'), nullable=True)
#     meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
#     meal_combination_id = Column(Integer, ForeignKey('meal_combinations.id'), nullable=False)
#     employee = relationship("Employee", back_populates="meal_selections")
#     third_party_participant = relationship("ThirdPartyParticipant", back_populates="meal_selections")
#     meal_combination = relationship("MealCombination", back_populates="meal_selections")
#     meeting = relationship("Meeting", back_populates="meal_selections")

# class MeetingParticipant(BaseTable):
#     __tablename__ = 'meeting_participants'
#     participant_type = Column(SQLAEnum(MeetingParticipantType), nullable=False)
#     employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     third_party_participant_id = Column(Integer, ForeignKey('third_party_participants.id'), nullable=True)
#     meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
#     employee = relationship("Employee", back_populates="meeting_participations")
#     third_party_participant = relationship("ThirdPartyParticipant", back_populates="meeting_participations")
#     meeting = relationship("Meeting", back_populates="participants")

# class MeetingAttendance(BaseTable):
#     __tablename__ = 'meeting_attendance'
#     meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
#     participant_type = Column(SQLAEnum(MeetingParticipantType), nullable=False)
#     employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     third_party_participant_id = Column(Integer, ForeignKey('third_party_participants.id'), nullable=True)
#     attended = Column(Boolean, default=False)
#     zoom_participation = Column(Boolean, default=False)
#     meeting = relationship("Meeting", back_populates="attendances")
#     employee = relationship("Employee")
#     third_party_participant = relationship("ThirdPartyParticipant")

# class MeetingMinutes(BaseTable):
#     __tablename__ = 'meeting_minutes'
#     meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
#     content = Column(Text, nullable=False)
#     meeting = relationship("Meeting", back_populates="minutes")

# class Meeting(BaseTable):
#     __tablename__ = 'meetings'
#     name = Column(String(255), nullable=False)
#     date_held = Column(DateTime, nullable=False)
#     meeting_type_id = Column(Integer, ForeignKey('meeting_types.id'))
#     meeting_type = relationship("MeetingType", back_populates="meetings")
#     organizer_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     organizer = relationship("Employee", back_populates="organized_meetings")
#     action_points = relationship("ActionPoint", back_populates="meeting", cascade="all, delete-orphan")
#     issues = relationship("IssueLog", back_populates="meeting")
#     meeting_category = Column(SQLAEnum(MeetingCategory), nullable=False)
#     is_meal_required = Column(Boolean, default=False, nullable=False)
#     is_third_party_required = Column(Boolean, default=False, nullable=False)
#     attendees = relationship("Employee", secondary=meeting_employee_association, back_populates="meetings")
#     third_party_attendees = relationship("ThirdPartyParticipant", secondary=meeting_thirdparty_association, back_populates="meetings")
#     meal_selections = relationship("MealSelection", back_populates="meeting", cascade="all, delete-orphan")
#     participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
#     attendances = relationship("MeetingAttendance", back_populates="meeting", cascade="all, delete-orphan")
#     minutes = relationship("MeetingMinutes", back_populates="meeting", cascade="all, delete-orphan")
#     third_party_participants = relationship("ThirdPartyParticipant", back_populates="meeting")

# # Project Model
# class Project(BaseTable):
#     __tablename__ = 'projects'
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=True)
#     tenancies = relationship("Tenancy", secondary=project_tenancy_association, back_populates="projects")
#     employees = relationship("Employee", secondary=project_employee_association, back_populates="projects")

# # Trip and Vehicle Models
# class Vehicle(BaseTable):
#     __tablename__ = 'vehicles'
#     name = Column(String(255))
#     licence_plate = Column(String(20), unique=True)
#     alternate_plate = Column(String(20), unique=True, nullable=True)
#     make = Column(String(100))
#     year = Column(Integer)
#     fuel_type = Column(String(50))
#     current_mileage = Column(DECIMAL(10, 2), nullable=True)
#     fuel_economy = Column(DECIMAL(10,2), nullable=True)
#     is_available = Column(Boolean, default=True)
#     seat_capacity = Column(Integer)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="vehicles")
#     maintenances = relationship("VehicleMaintenance", back_populates="vehicle")
#     trip = relationship("Trip", back_populates="vehicle")

# class VehicleMaintenance(BaseTable):
#     __tablename__ = 'vehicle_maintenances'
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
#     maintenance_type_id = Column(Integer, ForeignKey('maintenance_types.id'))
#     description = Column(Text)
#     cost = Column(DECIMAL(10, 2))
#     maintenance_date = Column(Date)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="vehicle_maintenances")
#     vehicle = relationship("Vehicle", back_populates="maintenances")
#     maintenance_type = relationship("MaintenanceType", back_populates="vehicle_maintenances")

# class MaintenanceType(BaseTable):
#     __tablename__ = 'maintenance_types'
#     name = Column(String(100), unique=True)
#     vehicle_maintenances = relationship("VehicleMaintenance", back_populates="maintenance_type")

# class FuelPurchase(BaseTable):
#     __tablename__ = 'fuel_purchases'
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
#     driver_id = Column(Integer, ForeignKey('drivers.id'))
#     quantity = Column(DECIMAL(10, 2))
#     unit_cost = Column(DECIMAL(10, 2))
#     total_cost = Column(DECIMAL(10, 2))
#     purchase_date = Column(Date)
#     file_path = Column(String, nullable=False)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="fuel_purchases")
#     vehicle = relationship("Vehicle", backref="fuel_purchases")
#     driver = relationship("Driver", back_populates="fuel_purchases")

# class Driver(BaseTable):
#     __tablename__ = 'drivers'
#     user_id = Column(Integer, ForeignKey('users.id'))
#     licence_number = Column(String(50), unique=True)
#     licence_exp_date = Column(Date)
#     is_available = Column(Boolean, default=True, nullable=True)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="drivers")
#     user = relationship("User", back_populates="driver")
#     fuel_purchases = relationship("FuelPurchase", back_populates="driver")
#     trip = relationship("Trip", back_populates="driver")

# class Trip(BaseTable):
#     __tablename__ = 'trips'
#     vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
#     driver_id = Column(Integer, ForeignKey('drivers.id'))
#     start_time = Column(DateTime, nullable=True)
#     actual_start_time = Column(DateTime, nullable=True)
#     end_time = Column(DateTime, nullable=True)
#     mileage_at_start = Column(DECIMAL(10, 2), nullable=True)
#     mileage_at_end = Column(DECIMAL(10, 2), nullable=True)
#     trip_code = Column(String(50), nullable=True)
#     distance = Column(DECIMAL(10, 2), nullable=True)
#     fuel_consumed = Column(DECIMAL(10, 2), nullable=True)
#     status = Column(String(50), default='Trip Scheduled')
#     issue_id = Column(Integer, ForeignKey('issue_logs.id'), nullable=True)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     tenancy = relationship("Tenancy", back_populates="trips")
#     driver = relationship("Driver", back_populates="trip", foreign_keys=[driver_id])
#     work_plans = relationship("WorkPlan", secondary=trip_workplan_association, back_populates="trips")
#     trip_report = relationship("TripReport", back_populates="trip", uselist=False)
#     vehicle = relationship("Vehicle", back_populates="trip", foreign_keys=[vehicle_id])
#     issue = relationship("IssueLog", back_populates="trip")

# class TripReport(BaseTable):
#     __tablename__ = 'trip_reports'
#     report_code = Column(String, nullable=True)
#     file_path = Column(String, nullable=True)
#     trip_id = Column(Integer, ForeignKey('trips.id'), unique=True)
#     workplan_id = Column(Integer, ForeignKey('work_plans.id'), nullable=True)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
#     is_submitted = Column(Boolean, nullable=True)
#     trip_completed = Column(Boolean, default=True, nullable=True)
#     reason = Column(Text, nullable=True)
#     trip = relationship("Trip", back_populates="trip_report", uselist=False)
#     work_plan = relationship("WorkPlan", back_populates="trip_report", uselist=False)
#     tenancy = relationship("Tenancy", back_populates="trip_reports")
#     trip_outcome = Column(Text, nullable=True)
#     observations = Column(Text, nullable=True)
#     summary = Column(Text, nullable=True)
#     issue_identified = Column(Boolean, default=False, nullable=True)

# # Issue and Action Models
# class IssueLogSource(BaseTable):
#     __tablename__ = 'issue_log_sources'
#     name = Column(String(100), nullable=False, unique=True)
#     issues = relationship("IssueLog", back_populates="source")

# class IssueStatus(BaseTable):
#     __tablename__ = 'issue_statuses'
#     status = Column(String(50), nullable=False, unique=True)
#     issues = relationship("IssueLog", back_populates="status")

# class IssueLog(BaseTable):
#     __tablename__ = 'issue_logs'
#     issue = Column(Text, nullable=False)
#     issue_description = Column(Text, nullable=True)
#     key_recommendation = Column(Text, nullable=True)
#     time_line_date = Column(Date, nullable=True)
#     notes_on_closure = Column(Text, nullable=True)
#     date_reported = Column(DateTime, default=datetime.datetime.utcnow)
#     close_date = Column(DateTime, nullable=True)
#     reported_by_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
#     thematic_area_id = Column(Integer, ForeignKey('thematic_areas.id'), nullable=True)
#     site_id = Column(Integer, ForeignKey('sites.id'), nullable=True)
#     source_id = Column(Integer, ForeignKey('issue_log_sources.id'))
#     status_id = Column(Integer, ForeignKey('issue_statuses.id'))
#     meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=True)
#     srt_id = Column(Integer, ForeignKey('srts.id'), nullable=True)
#     unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
#     department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
#     tenancy_id = Column(Integer, ForeignKey('tenancy.id'), nullable=False)
#     reported_by = relationship("Employee", foreign_keys=[reported_by_id], back_populates="issue_logs_reported")
#     thematic_area = relationship("ThematicArea", back_populates="issues")
#     site = relationship("Site", back_populates="issues")
#     source = relationship("IssueLogSource", back_populates="issues")
#     status = relationship("IssueStatus", back_populates="issues")
#     meeting = relationship("Meeting", back_populates="issues")
#     srt = relationship("SRT", back_populates="issues", foreign_keys=[srt_id])
#     unit = relationship("Unit", back_populates="issues", foreign_keys=[unit_id])
#     department = relationship("Department", back_populates="issues", foreign_keys=[department_id])
#     tenancy = relationship("Tenancy", back_populates="issues")
#     employees = relationship("Employee", secondary=focal_person_issue_association, back_populates="issues")
#     trip = relationship("Trip", back_populates="issue")

# class ActionPointSource(BaseTable):
#     __tablename__ = 'action_point_sources'
#     name = Column(String(100), nullable=False, unique=True)
#     action_points = relationship("ActionPoint", back_populates="source")

# class ActionPoint(BaseTable):
#     __tablename__ = 'action_points'
#     description = Column(Text, nullable=False)
#     responsible_id = Column(Integer, ForeignKey('employees.id'))
#     due_date = Column(Date)
#     completion_date = Column(Date)
#     status = Column(String(100))
#     action_point_source_id = Column(Integer, ForeignKey('action_point_sources.id'))
#     source = relationship("ActionPointSource", back_populates="action_points")
#     meeting_id = Column(Integer, ForeignKey('meetings.id'))
#     meeting = relationship("Meeting", back_populates="action_points")
#     responsible = relationship("Employee", foreign_keys=[responsible_id], back_populates="assigned_action_points")

# # Audit and Log Models
# class AuditLog(BaseTable):
#     __tablename__ = 'audit_logs'
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     action = Column(SQLAEnum(ActionEnum), nullable=False)
#     model = Column(String(50), nullable=False)
#     model_id = Column(Integer, nullable=False)
#     changes = Column(Text, nullable=True)
#     user = relationship("User", back_populates="audit_logs")

# # Call configure_mappers() after defining all models
# configure_mappers()




from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Text, Date, Table, Enum as SQLAEnum, Time
)
from sqlalchemy.orm import relationship, declarative_base, configure_mappers
from enum import Enum as PyEnum
import datetime
from db.database import Base

class BaseTable(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, default=True, comment="Soft delete flag")
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    date_updated = Column(DateTime, onupdate=datetime.datetime.utcnow, nullable=True)
    date_deleted = Column(DateTime, nullable=True)

class MeetingCategory(PyEnum):
    VIRTUAL = "Virtual Meeting"
    PHYSICAL = "Physical Meeting"

class ActionEnum(PyEnum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    SOFT_DELETE = "SOFT_DELETE"
    DELETE = "DELETE"
    CUSTOM_QUERY = "CUSTOM_QUERY"
    APPROVE = "APPROVE"
    DENY = "DENY"
    SCHEDULE_TRIP = "SCHEDULE_TRIP"
    RESCHEDULE = "RESCHEDULE"
    RESTORE = "RESTORE"
    REVIEW = "REVIEW"
    START_TRIP = "START_TRIP"
    END_TRIP = "END_TRIP"
    TRIP_REPORT_DOWNLOAD = "TRIP_REPORT_DOWNLOAD"  
    SUBMIT_TRIP_REPORT = "SUBMIT_TRIP_REPORT"  
    COMPLETED = "COMPLETED"
    RE_OPENED = "RE_OPENED"

class MealSelectionType(PyEnum):
    EMPLOYEE = "Employee"
    THIRD_PARTY = "Third Party"

class MeetingParticipantType(PyEnum):
    EMPLOYEE = "Employee"
    THIRD_PARTY = "Third Party"

# Association Tables
users_roles = Table(
    'users_roles', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('user_roles.id'), primary_key=True)
)

employee_srt_association = Table(
    'employee_srt', Base.metadata,
    Column('employee_id', ForeignKey('employees.id'), primary_key=True),
    Column('srt_id', ForeignKey('srts.id'), primary=True)
)

workplan_employee_association = Table(
    'workplan_employee', Base.metadata,
    Column('work_plan_id', ForeignKey('work_plans.id'), primary_key=True),
    Column('employee_id', ForeignKey('employees.id'), primary_key=True)
)

workplan_site_association = Table(
    'workplan_site_association', Base.metadata,
    Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True),
    Column('site_id', Integer, ForeignKey('sites.id'), primary_key=True)
)

trip_workplan_association = Table(
    'trip_workplan_association', Base.metadata,
    Column('trip_id', Integer, ForeignKey('trips.id'), primary_key=True),
    Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True)
)

workplan_location_association = Table(
    'workplan_location_association', Base.metadata,
    Column('work_plan_id', Integer, ForeignKey('work_plans.id'), primary_key=True),
    Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True)
)

focal_person_issue_association = Table(
    'focal_person_issue_association', Base.metadata,
    Column('issue_logs_id', Integer, ForeignKey('issue_logs.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)

task_employee_association = Table(
    'task_employee_association', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)

assignment_tenancy_association = Table(
    'assignment_tenancy_association', Base.metadata,
    Column('assignment_id', Integer, ForeignKey('assignments.id'), primary_key=True),
    Column('tenancy_id', Integer, ForeignKey('tenancy.id'), primary_key=True)
)

assignment_employee_association = Table(
    'assignment_employee_association', Base.metadata,
    Column('assignment_id', Integer, ForeignKey('assignments.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)

project_employee_association = Table(
    'project_employee_association', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)

project_tenancy_association = Table(
    'project_tenancy_association', Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('tenancy_id', Integer, ForeignKey('tenancy.id'), primary_key=True)
)

meeting_employee_association = Table(
    'meeting_employee_association', Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)

meeting_thirdparty_association = Table(
    'meeting_thirdparty_association', Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
    Column('thirdparty_id', Integer, ForeignKey('third_party_participants.id'), primary_key=True)
)

training_employee_association = Table(
    'training_employee_association', Base.metadata,
    Column('training_id', Integer, ForeignKey('trainings.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)

interview_employee_association = Table(
    'interview_employee_association', Base.metadata,
    Column('interview_id', Integer, ForeignKey('interviews.id'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True)
)
# User and Role Models
class UserRole(BaseTable):
    __tablename__ = 'user_roles'
    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", secondary=users_roles, back_populates="roles")

class User(BaseTable):
    __tablename__ = 'users'
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    reset_token = Column(String(100), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True, unique=True)
    roles = relationship("UserRole", secondary=users_roles, back_populates="users")
    employee = relationship("Employee", back_populates="user", uselist=False)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="users")
    driver = relationship("Driver", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    login_history = relationship("LoginHistory", back_populates="user")
    assignments = relationship("Assignment", back_populates="initiating_user")

class LoginHistory(BaseTable):
    __tablename__ = 'login_history'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    login_time = Column(DateTime, default=datetime.datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    user = relationship("User", back_populates="login_history")

class InvalidToken(BaseTable):
    __tablename__ = 'invalid_tokens'
    token = Column(String, nullable=False, unique=True)
    expiry_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User")

class Setting(BaseTable):
    __tablename__ = 'settings'
    setting_name = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=False)

# Tenancy and Organization Models
class Tenancy(BaseTable):
    __tablename__ = 'tenancy'
    name = Column(String(255), unique=True)
    locations = relationship("Location", back_populates="tenancy")
    sites = relationship("Site", back_populates="tenancy")
    srts = relationship("SRT", back_populates="tenancy")
    employees = relationship("Employee", back_populates="tenancy")
    vehicles = relationship("Vehicle", back_populates="tenancy")
    drivers = relationship("Driver", back_populates="tenancy")
    trips = relationship("Trip", back_populates="tenancy")
    trip_reports = relationship("TripReport", back_populates="tenancy")
    fuel_purchases = relationship("FuelPurchase", back_populates="tenancy")
    vehicle_maintenances = relationship("VehicleMaintenance", back_populates="tenancy")
    users = relationship("User", back_populates="tenancy")
    work_plans = relationship("WorkPlan", back_populates="tenancy")
    assignments = relationship("Assignment", secondary=assignment_tenancy_association, back_populates="tenancies")
    issues = relationship("IssueLog", back_populates="tenancy")
    projects = relationship("Project", secondary=project_tenancy_association, back_populates="tenancies")

class Department(BaseTable):
    __tablename__ = 'departments'
    name = Column(String(255), unique=True, nullable=False)
    employees = relationship("Employee", back_populates="department")
    units = relationship("Unit", back_populates="department")
    issues = relationship("IssueLog", back_populates="department")

class Unit(BaseTable):
    __tablename__ = 'units'
    name = Column(String(100), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    employees = relationship("Employee", back_populates="unit")
    department = relationship("Department", back_populates="units")
    issues = relationship("IssueLog", back_populates="unit")

class Employee(BaseTable):
    __tablename__ = 'employees'
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_number = Column(String(25), unique=True, nullable=False)
    staff_code = Column(String(100), unique=True, nullable=False)
    employee_email = Column(String(100), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    state_origin = Column(String(100), nullable=False)
    lga_origin = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    signature = Column(String, nullable=True)  # Adding signature field
    designation_id = Column(Integer, ForeignKey('designations.id'), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'), nullable=False)
    tenancy = relationship("Tenancy", back_populates="employees")
    designation = relationship("Designation", back_populates="employees")
    department = relationship("Department", back_populates="employees")
    unit = relationship("Unit", back_populates="employees")
    srts = relationship("SRT", secondary=employee_srt_association, back_populates="employees")
    user = relationship("User", back_populates="employee", uselist=False)
    led_work_plans = relationship("WorkPlan", back_populates="activity_lead")
    work_plans = relationship("WorkPlan", secondary=workplan_employee_association, back_populates="employees")
    issue_logs_reported = relationship("IssueLog", foreign_keys="IssueLog.reported_by_id")
    organized_meetings = relationship("Meeting", back_populates="organizer")
    assigned_action_points = relationship("ActionPoint", back_populates="responsible")
    tasks = relationship("Task", secondary=task_employee_association, back_populates="employees")
    led_assignments = relationship("Assignment", back_populates="assignment_lead")
    assignments = relationship("Assignment", secondary=assignment_employee_association, back_populates="responsible_employees")
    issues = relationship("IssueLog", secondary=focal_person_issue_association, back_populates="employees")
    milestones = relationship("Milestone", back_populates="responsible_employee")
    meetings = relationship("Meeting", secondary=meeting_employee_association, back_populates="attendees")
    meal_selections = relationship("MealSelection", back_populates="employee", cascade="all, delete-orphan")
    meeting_participations = relationship("MeetingParticipant", back_populates="employee")
    projects = relationship("Project", secondary=project_employee_association, back_populates="employees")

class Designation(BaseTable):
    __tablename__ = 'designations'
    name = Column(String(100), unique=True)
    employees = relationship("Employee", back_populates="designation")

class SRT(BaseTable):
    __tablename__ = 'srts'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="srts")
    employees = relationship("Employee", secondary=employee_srt_association, back_populates="srts")
    issues = relationship("IssueLog", back_populates="srt")

class Location(BaseTable):
    __tablename__ = 'locations'
    name = Column(String(255))
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="locations")
    sites = relationship("Site", back_populates="location")
    work_plans = relationship("WorkPlan", secondary=workplan_location_association, back_populates="locations")

class Site(BaseTable):
    __tablename__ = 'sites'
    name = Column(String(255), nullable=False)
    site_type = Column(String(100), nullable=False)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    tenancy = relationship("Tenancy", back_populates="sites")
    location = relationship("Location", back_populates="sites")
    issues = relationship("IssueLog", back_populates="site")
    work_plans = relationship("WorkPlan", secondary=workplan_site_association, back_populates="sites")
    third_party_participants = relationship("ThirdPartyParticipant", back_populates="site")

class ThematicArea(BaseTable):
    __tablename__ = 'thematic_areas'
    name = Column(String(255), nullable=False, unique=True)
    issues = relationship("IssueLog", back_populates="thematic_area")
    workplans = relationship("WorkPlan", back_populates="thematic_area")

# WorkPlan and Assignment Models
class WorkPlan(BaseTable):
    __tablename__ = 'work_plans'
    workplan_code = Column(String(20), nullable=True)
    activity_title = Column(String(255), nullable=False)
    specific_task = Column(Text, nullable=False)
    logistics_required = Column(String(100), nullable=True) 
    reason = Column(Text, nullable=True)
    status = Column(String(20), nullable=True)
    activity_start_time = Column(Time, nullable=True)
    activity_date = Column(Date, nullable=False)
    date_reviewed = Column(DateTime, nullable=True)
    date_approved = Column(DateTime, nullable=True)
    date_rescheduled = Column(DateTime, nullable=True)
    date_denied = Column(DateTime, nullable=True)
    is_rescheduled = Column(Boolean, default=False, nullable=False)
    is_denied = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    is_report_submitted = Column(Boolean, default=False, nullable=True)
    need_vehicle = Column(Boolean, default=False, nullable=True)
    vehicle_assigned = Column(Boolean, default=False, nullable=True)
    initiating_user_id = Column(Integer, ForeignKey('users.id'))
    initiating_unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    initiating_srt_id = Column(Integer, ForeignKey('srts.id'), nullable=True)
    initiating_department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    initiating_thematic_area_id = Column(Integer, ForeignKey('thematic_areas.id'), nullable=True)
    group_id = Column(Integer, nullable=True)
    initiating_user = relationship("User", foreign_keys=[initiating_user_id])
    reviewing_user = relationship("User", foreign_keys=[reviewed_by])
    approving_user = relationship("User", foreign_keys=[approved_by])
    initiating_unit = relationship("Unit", foreign_keys=[initiating_unit_id])
    initiating_srt = relationship("SRT", foreign_keys=[initiating_srt_id])
    initiating_department = relationship("Department", foreign_keys=[initiating_department_id])
    thematic_area = relationship("ThematicArea", foreign_keys=[initiating_thematic_area_id])
    workplan_source_id = Column(Integer, ForeignKey('workplan_sources.id'))
    workplan_source = relationship("WorkPlanSource", back_populates="workplans")
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="work_plans")
    activity_lead_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    activity_lead = relationship("Employee", back_populates="led_work_plans")
    trip_report = relationship("TripReport", back_populates="work_plan", uselist=False)
    sites = relationship("Site", secondary=workplan_site_association, back_populates="work_plans")
    employees = relationship("Employee", secondary=workplan_employee_association, back_populates="work_plans")
    trips = relationship("Trip", secondary=trip_workplan_association, back_populates="work_plans")
    locations = relationship("Location", secondary=workplan_location_association, back_populates="work_plans")

class WorkPlanSource(BaseTable):
    __tablename__ = 'workplan_sources'
    name = Column(String(100), unique=True)
    workplans = relationship("WorkPlan", back_populates="workplan_source")

class Assignment(BaseTable):
    __tablename__ = 'assignments'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Active")
    assignment_lead_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    initiating_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=True)
    date_completed = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    assignment_lead = relationship("Employee", back_populates="led_assignments")
    initiating_user = relationship("User", back_populates="assignments")
    tenancies = relationship("Tenancy", secondary=assignment_tenancy_association, back_populates="assignments")
    tasks = relationship("Task", back_populates="assignment")
    responsible_employees = relationship("Employee", secondary=assignment_employee_association, back_populates="assignments")
    milestones = relationship("Milestone", back_populates="assignment")

class Task(BaseTable):
    __tablename__ = 'tasks'
    description = Column(Text, nullable=False)
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    due_date = Column(Date, nullable=True)
    date_completed = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    status_id = Column(Integer, ForeignKey('task_statuses.id'), nullable=False)
    milestone_id = Column(Integer, ForeignKey('milestones.id'), nullable=True)
    comment = Column(Text, nullable=True)
    milestone = relationship("Milestone", back_populates="tasks")
    assignment = relationship("Assignment", back_populates="tasks")
    status = relationship("TaskStatus", back_populates="tasks")
    employees = relationship("Employee", secondary=task_employee_association, back_populates="tasks")

class TaskStatus(BaseTable):
    __tablename__ = 'task_statuses'
    name = Column(String(50), nullable=False, unique=True)
    tasks = relationship("Task", back_populates="status")

class Milestone(BaseTable):
    __tablename__ = 'milestones'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Pending")
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    responsible_employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    comment = Column(Text, nullable=True)
    date_completed = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    assignment = relationship("Assignment", back_populates="milestones")
    responsible_employee = relationship("Employee", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")

class Project(BaseTable):
    __tablename__ = 'projects'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    employees = relationship("Employee", secondary=project_employee_association, back_populates="projects")
    tenancies = relationship("Tenancy", secondary=project_tenancy_association, back_populates="projects")

# Meeting Models
class MeetingType(BaseTable):
    __tablename__ = 'meeting_types'
    name = Column(String(255), nullable=False, unique=True)
    meetings = relationship("Meeting", back_populates="meeting_type")

class Company(BaseTable):
    __tablename__ = 'companies'
    name = Column(String(255), nullable=False, unique=True)
    third_party_participants = relationship("ThirdPartyParticipant", back_populates="company")

class ThirdPartyParticipant(BaseTable):
    __tablename__ = 'third_party_participants'
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(50), nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=True)
    meal_selections = relationship("MealSelection", back_populates="third_party_participant", cascade="all, delete-orphan")
    company = relationship("Company", back_populates="third_party_participants")
    site = relationship("Site", back_populates="third_party_participants")
    meeting = relationship("Meeting", back_populates="third_party_participants")
    meeting_participations = relationship("MeetingParticipant", back_populates="third_party_participant")
    meetings = relationship("Meeting", secondary=meeting_thirdparty_association, back_populates="third_party_attendees")

class MealCombination(BaseTable):
    __tablename__ = 'meal_combinations'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    meal_selections = relationship("MealSelection", back_populates="meal_combination", cascade="all, delete-orphan")

class MealSelection(BaseTable):
    __tablename__ = 'meal_selections'
    selection_type = Column(SQLAEnum(MealSelectionType), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    third_party_participant_id = Column(Integer, ForeignKey('third_party_participants.id'), nullable=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    meal_combination_id = Column(Integer, ForeignKey('meal_combinations.id'), nullable=False)
    employee = relationship("Employee", back_populates="meal_selections")
    third_party_participant = relationship("ThirdPartyParticipant", back_populates="meal_selections")
    meal_combination = relationship("MealCombination", back_populates="meal_selections")
    meeting = relationship("Meeting", back_populates="meal_selections")

class MeetingParticipant(BaseTable):
    __tablename__ = 'meeting_participants'
    participant_type = Column(SQLAEnum(MeetingParticipantType), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    third_party_participant_id = Column(Integer, ForeignKey('third_party_participants.id'), nullable=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    employee = relationship("Employee", back_populates="meeting_participations")
    third_party_participant = relationship("ThirdPartyParticipant", back_populates="meeting_participations")
    meeting = relationship("Meeting", back_populates="participants")

class MeetingAttendance(BaseTable):
    __tablename__ = 'meeting_attendance'
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    participant_type = Column(SQLAEnum(MeetingParticipantType), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    third_party_participant_id = Column(Integer, ForeignKey('third_party_participants.id'), nullable=True)
    attended = Column(Boolean, default=False)
    meeting = relationship("Meeting", back_populates="attendances")
    employee = relationship("Employee")
    third_party_participant = relationship("ThirdPartyParticipant")

class MeetingMinutes(BaseTable):
    __tablename__ = 'meeting_minutes'
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    content = Column(Text, nullable=False)
    meeting = relationship("Meeting", back_populates="minutes")

class Meeting(BaseTable):
    __tablename__ = 'meetings'
    name = Column(String(255), nullable=False)
    date_held = Column(DateTime, nullable=False)
    meeting_type_id = Column(Integer, ForeignKey('meeting_types.id'))
    meeting_type = relationship("MeetingType", back_populates="meetings")
    organizer_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    organizer = relationship("Employee", back_populates="organized_meetings")
    action_points = relationship("ActionPoint", back_populates="meeting", cascade="all, delete-orphan")
    issues = relationship("IssueLog", back_populates="meeting")
    meeting_category = Column(SQLAEnum(MeetingCategory), nullable=False)
    zoom_meeting_id = Column(String(255), nullable=True)  # Adding Zoom meeting ID
    is_meal_required = Column(Boolean, default=False, nullable=False)
    is_third_party_required = Column(Boolean, default=False, nullable=False)
    attendees = relationship("Employee", secondary=meeting_employee_association, back_populates="meetings")
    third_party_attendees = relationship("ThirdPartyParticipant", secondary=meeting_thirdparty_association, back_populates="meetings")
    meal_selections = relationship("MealSelection", back_populates="meeting", cascade="all, delete-orphan")
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    attendances = relationship("MeetingAttendance", back_populates="meeting", cascade="all, delete-orphan")
    minutes = relationship("MeetingMinutes", back_populates="meeting", cascade="all, delete-orphan")
    third_party_participants = relationship("ThirdPartyParticipant", back_populates="meeting")

# Trip and Vehicle Models
class Vehicle(BaseTable):
    __tablename__ = 'vehicles'
    name = Column(String(255))
    licence_plate = Column(String(20), unique=True)
    alternate_plate = Column(String(20), unique=True, nullable=True)
    make = Column(String(100))
    year = Column(Integer)
    fuel_type = Column(String(50))
    current_mileage = Column(DECIMAL(10, 2), nullable=True)
    fuel_economy = Column(DECIMAL(10,2), nullable=True)
    is_available = Column(Boolean, default=True)
    seat_capacity = Column(Integer)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="vehicles")
    maintenances = relationship("VehicleMaintenance", back_populates="vehicle")
    trip = relationship("Trip", back_populates="vehicle")

class VehicleMaintenance(BaseTable):
    __tablename__ = 'vehicle_maintenances'
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    maintenance_type_id = Column(Integer, ForeignKey('maintenance_types.id'))
    description = Column(Text)
    cost = Column(DECIMAL(10, 2))
    maintenance_date = Column(Date)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="vehicle_maintenances")
    vehicle = relationship("Vehicle", back_populates="maintenances")
    maintenance_type = relationship("MaintenanceType", back_populates="vehicle_maintenances")

class MaintenanceType(BaseTable):
    __tablename__ = 'maintenance_types'
    name = Column(String(100), unique=True)
    vehicle_maintenances = relationship("VehicleMaintenance", back_populates="maintenance_type")

class FuelPurchase(BaseTable):
    __tablename__ = 'fuel_purchases'
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    quantity = Column(DECIMAL(10, 2))
    unit_cost = Column(DECIMAL(10, 2))
    total_cost = Column(DECIMAL(10, 2))
    purchase_date = Column(Date)
    file_path = Column(String, nullable=False)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="fuel_purchases")
    vehicle = relationship("Vehicle", backref="fuel_purchases")
    driver = relationship("Driver", back_populates="fuel_purchases")

class Driver(BaseTable):
    __tablename__ = 'drivers'
    user_id = Column(Integer, ForeignKey('users.id'))
    licence_number = Column(String(50), unique=True)
    licence_exp_date = Column(Date)
    is_available = Column(Boolean, default=True, nullable=True)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="drivers")
    user = relationship("User", back_populates="driver")
    fuel_purchases = relationship("FuelPurchase", back_populates="driver")
    trip = relationship("Trip", back_populates="driver")

class Trip(BaseTable):
    __tablename__ = 'trips'
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    start_time = Column(DateTime, nullable=True)
    actual_start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    mileage_at_start = Column(DECIMAL(10, 2), nullable=True)
    mileage_at_end = Column(DECIMAL(10, 2), nullable=True)
    trip_code = Column(String(50), nullable=True)
    distance = Column(DECIMAL(10, 2), nullable=True)
    fuel_consumed = Column(DECIMAL(10, 2), nullable=True)
    status = Column(String(50), default='Trip Scheduled')
    issue_id = Column(Integer, ForeignKey('issue_logs.id'), nullable=True)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    tenancy = relationship("Tenancy", back_populates="trips")
    driver = relationship("Driver", back_populates="trip", foreign_keys=[driver_id])
    work_plans = relationship("WorkPlan", secondary=trip_workplan_association, back_populates="trips")
    trip_report = relationship("TripReport", back_populates="trip", uselist=False)
    vehicle = relationship("Vehicle", back_populates="trip", foreign_keys=[vehicle_id])
    issue = relationship("IssueLog", back_populates="trip")

class TripReport(BaseTable):
    __tablename__ = 'trip_reports'
    report_code = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), unique=True)
    workplan_id = Column(Integer, ForeignKey('work_plans.id'), nullable=True)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'))
    is_submitted = Column(Boolean, nullable=True)
    trip_completed = Column(Boolean, default=True, nullable=True)
    reason = Column(Text, nullable=True)
    trip = relationship("Trip", back_populates="trip_report", uselist=False)
    work_plan = relationship("WorkPlan", back_populates="trip_report", uselist=False)
    tenancy = relationship("Tenancy", back_populates="trip_reports")
    trip_outcome = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    issue_identified = Column(Boolean, default=False, nullable=True)

# Issue and Action Models
class IssueLogSource(BaseTable):
    __tablename__ = 'issue_log_sources'
    name = Column(String(100), nullable=False, unique=True)
    issues = relationship("IssueLog", back_populates="source")

class IssueStatus(BaseTable):
    __tablename__ = 'issue_statuses'
    status = Column(String(50), nullable=False, unique=True)
    issues = relationship("IssueLog", back_populates="status")

class IssueLog(BaseTable):
    __tablename__ = 'issue_logs'
    issue = Column(Text, nullable=False)
    issue_description = Column(Text, nullable=True)
    key_recommendation = Column(Text, nullable=True)
    time_line_date = Column(Date, nullable=True)
    notes_on_closure = Column(Text, nullable=True)
    date_reported = Column(DateTime, default=datetime.datetime.utcnow)
    close_date = Column(DateTime, nullable=True)
    reported_by_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    thematic_area_id = Column(Integer, ForeignKey('thematic_areas.id'), nullable=True)
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=True)
    source_id = Column(Integer, ForeignKey('issue_log_sources.id'))
    status_id = Column(Integer, ForeignKey('issue_statuses.id'))
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=True)
    srt_id = Column(Integer, ForeignKey('srts.id'), nullable=True)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    tenancy_id = Column(Integer, ForeignKey('tenancy.id'), nullable=False)
    reported_by = relationship("Employee", foreign_keys=[reported_by_id], back_populates="issue_logs_reported")
    thematic_area = relationship("ThematicArea", back_populates="issues")
    site = relationship("Site", back_populates="issues")
    source = relationship("IssueLogSource", back_populates="issues")
    status = relationship("IssueStatus", back_populates="issues")
    meeting = relationship("Meeting", back_populates="issues")
    srt = relationship("SRT", back_populates="issues", foreign_keys=[srt_id])
    unit = relationship("Unit", back_populates="issues", foreign_keys=[unit_id])
    department = relationship("Department", back_populates="issues", foreign_keys=[department_id])
    tenancy = relationship("Tenancy", back_populates="issues")
    employees = relationship("Employee", secondary=focal_person_issue_association, back_populates="issues")
    trip = relationship("Trip", back_populates="issue")

class ActionPointSource(BaseTable):
    __tablename__ = 'action_point_sources'
    name = Column(String(100), nullable=False, unique=True)
    action_points = relationship("ActionPoint", back_populates="source")

class ActionPoint(BaseTable):
    __tablename__ = 'action_points'
    description = Column(Text, nullable=False)
    responsible_id = Column(Integer, ForeignKey('employees.id'))
    due_date = Column(Date)
    completion_date = Column(Date)
    status = Column(String(100))
    action_point_source_id = Column(Integer, ForeignKey('action_point_sources.id'))
    source = relationship("ActionPointSource", back_populates="action_points")
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    meeting = relationship("Meeting", back_populates="action_points")
    responsible = relationship("Employee", foreign_keys=[responsible_id], back_populates="assigned_action_points")

# Audit and Log Models
class AuditLog(BaseTable):
    __tablename__ = 'audit_logs'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(SQLAEnum(ActionEnum), nullable=False)
    model = Column(String(50), nullable=False)
    model_id = Column(Integer, nullable=False)
    changes = Column(Text, nullable=True)
    user = relationship("User", back_populates="audit_logs")

# Human Resource Models
class Document(BaseTable):
    __tablename__ = 'documents'
    name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_path = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="documents")

class JobOpening(BaseTable):
    __tablename__ = 'job_openings'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    status = Column(String(50), default="Open", nullable=False)
    applicants = relationship("Applicant", back_populates="job_opening")

class Applicant(BaseTable):
    __tablename__ = 'applicants'
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(50), nullable=False)
    resume_path = Column(String, nullable=False)
    job_opening_id = Column(Integer, ForeignKey('job_openings.id'), nullable=False)
    job_opening = relationship("JobOpening", back_populates="applicants")
    interviews = relationship("Interview", back_populates="applicant")

class Interview(BaseTable):
    __tablename__ = 'interviews'
    date_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)
    feedback = Column(Text, nullable=True)
    applicant_id = Column(Integer, ForeignKey('applicants.id'), nullable=False)
    applicant = relationship("Applicant", back_populates="interviews")
    interviewers = relationship("Employee", secondary="interview_employee_association", back_populates="interviews")


class PerformanceReview(BaseTable):
    __tablename__ = 'performance_reviews'
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    comments = Column(Text, nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performance_reviews")
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])

class Training(BaseTable):
    __tablename__ = 'trainings'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)
    employees = relationship("Employee", secondary="training_employee_association", back_populates="trainings")



class LeaveRequest(BaseTable):
    __tablename__ = 'leave_requests'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="leave_requests")

class   Attendance(BaseTable):
    __tablename__ = 'attendance'
    date = Column(Date, nullable=False)
    clock_in_time = Column(Time, nullable=True)
    clock_out_time = Column(Time, nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="attendance_records")

class Payroll(BaseTable):
    __tablename__ = 'payroll'
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
   # salary = Column(DECIMAL(10, 2), nullable=False)
    bonuses = Column(DECIMAL(10, 2), nullable=True)
    housing_allowance=Column(DECIMAL(10,2),nullable=False)
    base_salary= Column(DECIMAL(10,2), nullable=True)
    #deductions = Column(DECIMAL(10, 2), nullable=True)
    payee_decuction=Column(DECIMAL(10,2))
    
    net_pay = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    employee = relationship("Employee", back_populates="payroll_records")

class Benefit(BaseTable):
    __tablename__ = 'benefits'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="benefits")

class HRReport(BaseTable):
    __tablename__ = 'hr_reports'
    report_type = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    generated_date = Column(Date, nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    employee = relationship("Employee", back_populates="hr_reports")

# Call configure_mappers() after defining all models
configure_mappers()
