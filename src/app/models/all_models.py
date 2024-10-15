from sqlalchemy import (
    CheckConstraint,
    Column,
    Index,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    DECIMAL,
    Text,
    Date,
    Table,
    Enum as SQLAEnum,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref, declarative_base, configure_mappers
from enum import Enum as PyEnum
import datetime
from db.database import Base



# Base Model
class BaseTable(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, default=True, comment="Soft delete flag")
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    date_updated = Column(DateTime, onupdate=datetime.datetime.utcnow, nullable=True)
    date_deleted = Column(DateTime, nullable=True)


# Enums
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
    VIEW="VIEW"


class MealSelectionType(PyEnum):
    EMPLOYEE = "Employee"
    THIRD_PARTY = "Third Party"


class MeetingParticipantType(PyEnum):
    EMPLOYEE = "Employee"
    THIRD_PARTY = "Third Party"


# Association Tables
users_roles = Table(
    "users_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("user_roles.id"), primary_key=True),
)

employee_srt_association = Table(
    "employee_srt",
    Base.metadata,
    Column("employee_id", ForeignKey("employees.id"), primary_key=True),
    Column("srt_id", ForeignKey("srts.id"), primary_key=True),
)

workplan_employee_association = Table(
    "workplan_employee",
    Base.metadata,
    Column("work_plan_id", ForeignKey("work_plans.id"), primary_key=True),
    Column("employee_id", ForeignKey("employees.id"), primary_key=True),
)

workplan_site_association = Table(
    "workplan_site_association",
    Base.metadata,
    Column("work_plan_id", Integer, ForeignKey("work_plans.id"), primary_key=True),
    Column("site_id", Integer, ForeignKey("sites.id"), primary_key=True),
)

trip_workplan_association = Table(
    "trip_workplan_association",
    Base.metadata,
    Column("trip_id", Integer, ForeignKey("trips.id"), primary_key=True),
    Column("work_plan_id", Integer, ForeignKey("work_plans.id"), primary_key=True),
)

trip_employee_association = Table(
    "trip_employee_association",
    Base.metadata,
    Column("trip_id", Integer, ForeignKey("trips.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

workplan_location_association = Table(
    "workplan_location_association",
    Base.metadata,
    Column("work_plan_id", Integer, ForeignKey("work_plans.id"), primary_key=True),
    Column("location_id", Integer, ForeignKey("locations.id"), primary_key=True),
)

focal_person_issue_association = Table(
    "focal_person_issue_association",
    Base.metadata,
    Column("issue_logs_id", Integer, ForeignKey("issue_logs.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

task_employee_association = Table(
    "task_employee_association",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

assignment_tenancy_association = Table(
    "assignment_tenancy_association",
    Base.metadata,
    Column("assignment_id", Integer, ForeignKey("assignments.id"), primary_key=True),
    Column("tenancy_id", Integer, ForeignKey("tenancy.id"), primary_key=True),
)

assignment_employee_association = Table(
    "assignment_employee_association",
    Base.metadata,
    Column("assignment_id", Integer, ForeignKey("assignments.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

meeting_employee_association = Table(
    "meeting_employee_association",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

meeting_thirdparty_association = Table(
    "meeting_thirdparty_association",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id"), primary_key=True),
    Column(
        "thirdparty_id",
        Integer,
        ForeignKey("third_party_participants.id"),
        primary_key=True,
    ),
)

training_employee_association = Table(
    "training_employee_association",
    Base.metadata,
    Column("training_id", Integer, ForeignKey("trainings.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

project_tenancy_association = Table(
    "project_tenancy_association",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("tenancy_id", Integer, ForeignKey("tenancy.id"), primary_key=True),
)

project_employee_association = Table(
    "project_employee_association",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

meeting_coordinator_association = Table(
    "meeting_coordinator_association",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

meeting_moderator_association = Table(
    "meeting_moderator_association",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meetings.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

scope_of_work_employee_association = Table(
    "scope_of_work_employee",
    Base.metadata,
    Column(
        "scope_of_work_id", Integer, ForeignKey("scope_of_works.id"), primary_key=True
    ),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

scope_of_work_line_item_employee_association = Table(
    "scope_of_work_line_item_employee",
    Base.metadata,
    Column(
        "line_item_id",
        Integer,
        ForeignKey("scope_of_work_line_items.id"),
        primary_key=True,
    ),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)

# # Indexing email and license plate for fast look-up
# Index('ix_users_email', User.email)
# Index('ix_vehicles_licence_plate', Vehicle.licence_plate)


# User and Role Models

# class UserRole(BaseTable):
#     __tablename__ = "user_roles"
#     # id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(50), unique=True, nullable=False)
#     description = Column(Text, nullable=True)

#     # Relationships
#     users = relationship("User", secondary=users_roles, back_populates="roles")
#     approval_steps = relationship("ApprovalStep", back_populates="role")


class UserRole(BaseTable):
    __tablename__ = "user_roles"
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", secondary=users_roles, back_populates="roles")
    approval_steps = relationship("ApprovalStep", back_populates="role")
    
    # Relationship with RouteRole to define accessible routes for each role
    route_roles = relationship("RouteRole", back_populates="role")


class Route(BaseTable):
    __tablename__ = "routes"
    
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # e.g., 'GET', 'POST', etc.
    description = Column(String, nullable=True)
    # Unique constraint to ensure each path-method combination is unique
    __table_args__ = (UniqueConstraint("path", "method", name="uix_path_method"),)
    
    # Relationship with RouteRole to define roles that have access to this route
    route_roles = relationship("RouteRole", back_populates="route")
    module_id = Column(Integer, ForeignKey('modules.id'))
    
    module = relationship("Module", back_populates="routes")

class RouteRole(Base):
    __tablename__ = "route_roles"
    
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("user_roles.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    route = relationship("Route", back_populates="route_roles")
    role = relationship("UserRole", back_populates="route_roles")


class User(BaseTable):
    __tablename__ = "users"
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    reset_token = Column(String(100), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=True, unique=True
    )
    roles = relationship("UserRole", secondary=users_roles, back_populates="users")
    employee = relationship("Employee", back_populates="user", uselist=False)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="users")
    driver = relationship("Driver", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    login_history = relationship("LoginHistory", back_populates="user")
    assignments = relationship("Assignment", back_populates="initiating_user")
    approval_logs = relationship("ApprovalLog", back_populates="user")
    __table_args__ = (Index("ix_users_email", "email"),)

    # def __repr__(self):
    #     return f"<User(id={self.id}, username={self.username}, email={self.email})>"

class LoginHistory(BaseTable):
    __tablename__ = "login_history"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_time = Column(DateTime, default=datetime.datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    user = relationship("User", back_populates="login_history")


class InvalidToken(BaseTable):
    __tablename__ = "invalid_tokens"
    token = Column(String, nullable=False, unique=True)
    expiry_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")


class Setting(BaseTable):
    __tablename__ = "settings"
    setting_name = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=False)


# Tenancy and Organization Models
class Tenancy(BaseTable):
    __tablename__ = "tenancy"
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
    assignments = relationship(
        "Assignment",
        secondary=assignment_tenancy_association,
        back_populates="tenancies",
    )
    issues = relationship("IssueLog", back_populates="tenancy")
    projects = relationship(
        "Project", secondary=project_tenancy_association, back_populates="tenancies"
    )
    companies = relationship("Company", back_populates="tenancy")
    #start_locations = relationship("TripStartLocation", back_populates="tenancy")
    special_locations = relationship("TripSpecialLocation", back_populates="tenancy")


class Department(BaseTable):
    __tablename__ = "departments"
    name = Column(String(255), unique=True, nullable=False)
    employees = relationship("Employee", back_populates="department")
    units = relationship("Unit", back_populates="department")
    issues = relationship("IssueLog", back_populates="department")
    job_openings = relationship("JobOpening", back_populates="department")


class Unit(BaseTable):
    __tablename__ = "units"
    name = Column(String(100), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    employees = relationship("Employee", back_populates="unit")
    department = relationship("Department", back_populates="units")
    issues = relationship("IssueLog", back_populates="unit")


class Designation(BaseTable):
    __tablename__ = "designations"
    name = Column(String(100), unique=True)
    employees = relationship("Employee", back_populates="designation")


class SRT(BaseTable):
    __tablename__ = "srts"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="srts")
    employees = relationship(
        "Employee", secondary=employee_srt_association, back_populates="srts"
    )
    issues = relationship("IssueLog", back_populates="srt")


class Location(BaseTable):
    __tablename__ = "locations"
    name = Column(String(255))
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="locations")
    sites = relationship("Site", back_populates="location")
    work_plans = relationship(
        "WorkPlan", secondary=workplan_location_association, back_populates="locations"
    )


class Site(BaseTable):
    __tablename__ = "sites"
    name = Column(String(255), nullable=False)
    site_type = Column(String(100), nullable=False)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    tenancy = relationship("Tenancy", back_populates="sites")
    location = relationship("Location", back_populates="sites")
    issues = relationship("IssueLog", back_populates="site")
    work_plans = relationship(
        "WorkPlan", secondary=workplan_site_association, back_populates="sites"
    )
    third_party_participants = relationship(
        "ThirdPartyParticipant", back_populates="site"
    )
    trip_stages = relationship("TripStage", back_populates="site")


class ThematicArea(BaseTable):
    __tablename__ = "thematic_areas"
    name = Column(String(255), nullable=False, unique=True)
    issues = relationship("IssueLog", back_populates="thematic_area")
    work_plans = relationship("WorkPlan", back_populates="thematic_area")

class ScopeOfWorkLineItem(BaseTable):
    __tablename__ = 'scope_of_work_line_items'
    scope_of_work_id = Column(Integer, ForeignKey('scope_of_works.id'), nullable=False)
    description = Column(Text, nullable=False)
    employees = relationship("Employee", secondary=scope_of_work_line_item_employee_association, back_populates="line_items")
    scope_of_work = relationship("ScopeOfWork", back_populates="line_items")

class ScopeOfWork(BaseTable):
    __tablename__ = 'scope_of_works'
    work_plan_id = Column(Integer, ForeignKey('work_plans.id'), nullable=False)
    description = Column(Text, nullable=False)
    work_plan = relationship("WorkPlan", back_populates="scopes_of_work")
    employees = relationship("Employee", secondary=scope_of_work_employee_association, back_populates="scopes_of_work")
    line_items = relationship("ScopeOfWorkLineItem", back_populates="scope_of_work")


class ApprovalFlow(BaseTable):
    __tablename__ = "approval_flows"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)

    # Relationships
    module = relationship('Module', back_populates='approval_flows')
    # steps = relationship("ApprovalStep", back_populates="flow", cascade="all, delete-orphan")
    steps = relationship("ApprovalStep", back_populates="approval_flow", cascade="all, delete-orphan")
    work_plans = relationship("WorkPlan", back_populates="approval_flow")
    trips = relationship("Trip", back_populates="approval_flow")
    timesheets = relationship("Timesheet", back_populates="approval_flow")
    leave_requests = relationship("LeaveRequest", back_populates="approval_flow")
    personal_development_reviews = relationship("PersonalDevelopmentReview", back_populates="approval_flow")

    def __repr__(self):
        return f"<ApprovalFlow(name={self.name}, description={self.description})>"


class ApprovalStep(BaseTable):
    __tablename__ = "approval_steps"
    
    flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=False)
    action = Column(SQLAEnum(ActionEnum), nullable=False, default=ActionEnum.REVIEW)
    description = Column(String, nullable=True)  # Add this line    
    # Relationships
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)

    # Relationship to the Module
    module = relationship("Module", back_populates="approval_steps")
    # flow = relationship("ApprovalFlow", back_populates="steps")
    # Relationship to ApprovalFlow
    approval_flow = relationship("ApprovalFlow", back_populates="steps")
    
    role = relationship("UserRole", back_populates="approval_steps")
    logs = relationship("ApprovalLog", back_populates="step", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_approval_steps_flow_id_step_order", "flow_id", "step_order"),
    )


class Module(BaseTable):
    __tablename__ = 'modules'

    
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # # Establishing a relationship with the ApprovalFlow model
    # approval_flows = relationship('ApprovalFlow', back_populates='module')
    # Establish a one-to-many relationship with ApprovalFlow
    approval_flows = relationship(
        "ApprovalFlow",
        back_populates="module",
        cascade="all, delete-orphan"
    )

    # Establish a one-to-many relationship with ApprovalStep (optional)
    # This assumes that each step is directly associated with a module
    approval_steps = relationship(
        "ApprovalStep",
        back_populates="module",
        cascade="all, delete-orphan"
    )
    routes = relationship("Route", back_populates="module")

    def __repr__(self):
        return f"<Module(name={self.name}, description={self.description})>"


class ApprovalLog(BaseTable):
    __tablename__ = "approval_logs"
    
    step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="Pending")
    comments = Column(Text, nullable=True)
    date_actioned = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign keys for relationships to modules that require approval
    work_plan_id = Column(Integer, ForeignKey("work_plans.id"), nullable=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    timesheet_id = Column(Integer, ForeignKey("timesheets.id"), nullable=True)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=True)
    personal_development_review_id = Column(Integer, ForeignKey("personal_development_reviews.id"), nullable=True)

    # Relationships
    step = relationship("ApprovalStep", back_populates="logs")
    user = relationship("User")
    work_plan = relationship("WorkPlan", back_populates="approval_logs")
    trip = relationship("Trip", back_populates="approval_logs")
    timesheet = relationship("Timesheet", back_populates="approval_logs")
    leave_request = relationship("LeaveRequest", back_populates="approval_logs")
    personal_development_review = relationship("PersonalDevelopmentReview", back_populates="approval_logs")

    def __repr__(self):
        return f"<ApprovalLog(step_id={self.step_id}, approved_by_id={self.approved_by_id}, status={self.status})>"


class WorkPlan(BaseTable):
    __tablename__ = "work_plans"
    
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
    is_report_submitted = Column(Boolean, nullable=True)
    need_vehicle = Column(Boolean, nullable=True)
    vehicle_assigned = Column(Boolean, nullable=True)

    # Approval workflow fields
    approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
    current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)

    # Relationships for approval workflow
    approval_flow = relationship("ApprovalFlow", back_populates="work_plans")
    current_step = relationship("ApprovalStep")
    approval_logs = relationship("ApprovalLog", back_populates="work_plan")

    # Existing foreign key relationships
    initiating_user_id = Column(Integer, ForeignKey("users.id"))
    initiating_unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    initiating_srt_id = Column(Integer, ForeignKey("srts.id"), nullable=True)
    initiating_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    initiating_thematic_area_id = Column(Integer, ForeignKey("thematic_areas.id"), nullable=True)
    workplan_source_id = Column(Integer, ForeignKey("workplan_sources.id"))
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    activity_lead_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Relationship mappings
    initiating_user = relationship("User", foreign_keys=[initiating_user_id])
    reviewing_user = relationship("User", foreign_keys=[reviewed_by])
    approving_user = relationship("User", foreign_keys=[approved_by])
    initiating_unit = relationship("Unit", foreign_keys=[initiating_unit_id])
    initiating_srt = relationship("SRT", foreign_keys=[initiating_srt_id])
    initiating_department = relationship("Department", foreign_keys=[initiating_department_id])
    thematic_area = relationship("ThematicArea", foreign_keys=[initiating_thematic_area_id])
    workplan_source = relationship("WorkPlanSource", back_populates="work_plans")
    tenancy = relationship("Tenancy", back_populates="work_plans")
    activity_lead = relationship("Employee", back_populates="led_work_plans")
    project = relationship("Project", back_populates="work_plans")
    
    trip_report = relationship("TripReport", back_populates="work_plan", uselist=False)
    sites = relationship("Site", secondary=workplan_site_association, back_populates="work_plans")
    employees = relationship("Employee", secondary=workplan_employee_association, back_populates="work_plans")
    trips = relationship("Trip", secondary=trip_workplan_association, back_populates="work_plans")
    locations = relationship("Location", secondary=workplan_location_association, back_populates="work_plans")
    scopes_of_work = relationship("ScopeOfWork", back_populates="work_plan")

    def submit_for_approval(self):
        if not self.approval_flow:
            raise ValueError("An approval flow must be set before submitting for approval.")
        # Logic to initiate the approval process
        # You can set the current_step to the first step in the approval flow, for example
        self.current_step = self.approval_flow.steps[0] if self.approval_flow.steps else None

    def __repr__(self):
        return f"<WorkPlan(workplan_code={self.workplan_code}, status={self.status})>"



class WorkPlanSource(BaseTable):
    __tablename__ = "workplan_sources"
    name = Column(String(100), unique=True)
    work_plans = relationship("WorkPlan", back_populates="workplan_source")


class Assignment(BaseTable):
    __tablename__ = "assignments"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Active")
    assignment_lead_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    initiating_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=True)
    date_completed = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    assignment_lead = relationship("Employee", back_populates="led_assignments")
    initiating_user = relationship("User", back_populates="assignments")
    tenancies = relationship(
        "Tenancy",
        secondary=assignment_tenancy_association,
        back_populates="assignments",
    )
    tasks = relationship("Task", back_populates="assignment")
    responsible_employees = relationship(
        "Employee",
        secondary=assignment_employee_association,
        back_populates="assignments",
    )
    milestones = relationship("Milestone", back_populates="assignment")


class Task(BaseTable):
    __tablename__ = "tasks"
    description = Column(Text, nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    due_date = Column(Date, nullable=True)
    date_completed = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    status_id = Column(Integer, ForeignKey("task_statuses.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    comment = Column(Text, nullable=True)
    milestone = relationship("Milestone", back_populates="tasks")
    assignment = relationship("Assignment", back_populates="tasks")
    status = relationship("TaskStatus", back_populates="tasks")
    employees = relationship(
        "Employee", secondary=task_employee_association, back_populates="tasks"
    )


class TaskStatus(BaseTable):
    __tablename__ = "task_statuses"
    name = Column(String(50), nullable=False, unique=True)
    tasks = relationship("Task", back_populates="status")


class Milestone(BaseTable):
    __tablename__ = "milestones"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Pending")
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    responsible_employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False
    )
    comment = Column(Text, nullable=True)
    date_completed = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    assignment = relationship("Assignment", back_populates="milestones")
    responsible_employee = relationship("Employee", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")


# Meeting Models
class MeetingType(BaseTable):
    __tablename__ = "meeting_types"
    name = Column(String(255), nullable=False, unique=True)
    meetings = relationship("Meeting", back_populates="meeting_type")


class Company(BaseTable):
    __tablename__ = "companies"
    name = Column(String(255), nullable=False, unique=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"), nullable=True)
    tenancy = relationship("Tenancy", back_populates="companies")
    third_party_participants = relationship(
        "ThirdPartyParticipant", back_populates="company"
    )


class ThirdPartyParticipant(BaseTable):
    __tablename__ = "third_party_participants"
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(50), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    meal_selections = relationship(
        "MealSelection",
        back_populates="third_party_participant",
        cascade="all, delete-orphan",
    )
    company = relationship("Company", back_populates="third_party_participants")
    site = relationship("Site", back_populates="third_party_participants")
    meeting = relationship("Meeting", back_populates="third_party_participants")
    meeting_participations = relationship(
        "MeetingParticipant", back_populates="third_party_participant"
    )
    meetings = relationship(
        "Meeting",
        secondary=meeting_thirdparty_association,
        back_populates="third_party_attendees",
    )


class MealCombination(BaseTable):
    __tablename__ = "meal_combinations"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    meal_selections = relationship(
        "MealSelection", back_populates="meal_combination", cascade="all, delete-orphan"
    )


class MealSelection(BaseTable):
    __tablename__ = "meal_selections"
    selection_type = Column(SQLAEnum(MealSelectionType), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    third_party_participant_id = Column(
        Integer, ForeignKey("third_party_participants.id"), nullable=True
    )
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    meal_combination_id = Column(
        Integer, ForeignKey("meal_combinations.id"), nullable=False
    )
    employee = relationship("Employee", back_populates="meal_selections")
    third_party_participant = relationship(
        "ThirdPartyParticipant", back_populates="meal_selections"
    )
    meal_combination = relationship("MealCombination", back_populates="meal_selections")
    meeting = relationship("Meeting", back_populates="meal_selections")


class MeetingParticipant(BaseTable):
    __tablename__ = "meeting_participants"
    participant_type = Column(SQLAEnum(MeetingParticipantType), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    third_party_participant_id = Column(
        Integer, ForeignKey("third_party_participants.id"), nullable=True
    )
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    employee = relationship("Employee", back_populates="meeting_participations")
    third_party_participant = relationship(
        "ThirdPartyParticipant", back_populates="meeting_participations"
    )
    meeting = relationship("Meeting", back_populates="participants")


class MeetingAttendance(BaseTable):
    __tablename__ = "meeting_attendance"
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    participant_type = Column(SQLAEnum(MeetingParticipantType), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    third_party_participant_id = Column(
        Integer, ForeignKey("third_party_participants.id"), nullable=True
    )
    attended = Column(Boolean, default=False)
    date = Column(Date, nullable=False)
    clock_in_time = Column(Time, nullable=True)
    clock_out_time = Column(Time, nullable=True)
    meeting = relationship("Meeting", back_populates="attendances")
    employee = relationship("Employee")
    third_party_participant = relationship("ThirdPartyParticipant")


class MeetingMinutes(BaseTable):
    __tablename__ = "meeting_minutes"
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    content = Column(Text, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employee = relationship("Employee", back_populates="meeting_minutes")
    meeting = relationship("Meeting", back_populates="minutes")


class Meeting(BaseTable):
    __tablename__ = "meetings"
    name = Column(String(255), nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    meeting_type_id = Column(Integer, ForeignKey("meeting_types.id"))
    meeting_type = relationship("MeetingType", back_populates="meetings")
    organizer_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    organizer = relationship("Employee", back_populates="organized_meetings")
    action_points = relationship(
        "ActionPoint", back_populates="meeting", cascade="all, delete-orphan"
    )
    issues = relationship("IssueLog", back_populates="meeting")
    meeting_category = Column(SQLAEnum(MeetingCategory), nullable=False)
    is_meal_required = Column(Boolean, default=False, nullable=False)
    is_third_party_required = Column(Boolean, default=False, nullable=False)
    attendees = relationship(
        "Employee", secondary=meeting_employee_association, back_populates="meetings"
    )
    third_party_attendees = relationship(
        "ThirdPartyParticipant",
        secondary=meeting_thirdparty_association,
        back_populates="meetings",
    )
    meal_selections = relationship(
        "MealSelection", back_populates="meeting", cascade="all, delete-orphan"
    )
    participants = relationship(
        "MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan"
    )
    attendances = relationship(
        "MeetingAttendance", back_populates="meeting", cascade="all, delete-orphan"
    )
    minutes = relationship(
        "MeetingMinutes", back_populates="meeting", cascade="all, delete-orphan"
    )
    third_party_participants = relationship(
        "ThirdPartyParticipant", back_populates="meeting"
    )
    coordinators = relationship(
        "Employee",
        secondary=meeting_coordinator_association,
        back_populates="coordinated_meetings",
    )
    moderators = relationship(
        "Employee",
        secondary=meeting_moderator_association,
        back_populates="moderated_meetings",
    )
    zoom_meeting_id = Column(String(255), nullable=True)
    zoom_participant_report = Column(Text, nullable=True)


# Trip and Vehicle Models
class Vehicle(BaseTable):
    __tablename__ = "vehicles"
    name = Column(String(255))
    licence_plate = Column(String(20), unique=True)
    alternate_plate = Column(String(20), unique=True, nullable=True)
    make = Column(String(100))
    year = Column(Integer)
    fuel_type = Column(String(50))
    current_mileage = Column(DECIMAL(10, 2), nullable=True)
    fuel_economy = Column(DECIMAL(10, 2), nullable=True)
    is_available = Column(Boolean, default=True)
    seat_capacity = Column(Integer)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="vehicles")
    maintenances = relationship("VehicleMaintenance", back_populates="vehicle")
    trip = relationship("Trip", back_populates="vehicle")
    __table_args__ = (Index("ix_vehicles_licence_plate", "licence_plate"),)


class VehicleMaintenance(BaseTable):
    __tablename__ = "vehicle_maintenances"
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    maintenance_type_id = Column(Integer, ForeignKey("maintenance_types.id"))
    description = Column(Text)
    cost = Column(DECIMAL(10, 2))
    maintenance_date = Column(Date)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="vehicle_maintenances")
    vehicle = relationship("Vehicle", back_populates="maintenances")
    maintenance_type = relationship(
        "MaintenanceType", back_populates="vehicle_maintenances"
    )


class MaintenanceType(BaseTable):
    __tablename__ = "maintenance_types"
    name = Column(String(100), unique=True)
    vehicle_maintenances = relationship(
        "VehicleMaintenance", back_populates="maintenance_type"
    )

class FuelPurchase(BaseTable):
    __tablename__ = "fuel_purchases"
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    quantity = Column(DECIMAL(10, 2))
    unit_cost = Column(DECIMAL(10, 2))
    total_cost = Column(DECIMAL(10, 2))
    purchase_date = Column(Date)
    file_path = Column(String, nullable=False)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="fuel_purchases")
    vehicle = relationship("Vehicle", backref="fuel_purchases")
    driver = relationship("Driver", back_populates="fuel_purchases")


class Driver(BaseTable):
    __tablename__ = "drivers"
    user_id = Column(Integer, ForeignKey("users.id"))
    licence_number = Column(String(50), unique=True)
    licence_exp_date = Column(Date)
    is_available = Column(Boolean, default=True, nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="drivers")
    user = relationship("User", back_populates="driver")
    fuel_purchases = relationship("FuelPurchase", back_populates="driver")
    trip = relationship("Trip", back_populates="driver")


class Trip(BaseTable):
    __tablename__ = "trips"
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    start_time = Column(DateTime, nullable=True)
    actual_start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    mileage_at_start = Column(DECIMAL(10, 2), nullable=True)
    mileage_at_end = Column(DECIMAL(10, 2), nullable=True)
    trip_code = Column(String(50), nullable=True)
    distance = Column(DECIMAL(10, 2), nullable=True)
    fuel_consumed = Column(DECIMAL(10, 2), nullable=True)
    status = Column(String(50), default="Trip Scheduled")
    issue_id = Column(Integer, ForeignKey("issue_logs.id"), nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    trip_start_location_id = Column(Integer, ForeignKey("trip_special_locations.id"), nullable=True)
    trip_end_location_id = Column(Integer, ForeignKey("trip_special_locations.id"), nullable=True)

    # Approval workflow fields
    approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
    current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)

    # Relationships for approval workflow
    approval_flow = relationship("ApprovalFlow", back_populates="trips")
    current_step = relationship("ApprovalStep")
    approval_logs = relationship("ApprovalLog", back_populates="trip")

    # Existing relationships
    tenancy = relationship("Tenancy", back_populates="trips")
    driver = relationship("Driver", back_populates="trip", foreign_keys=[driver_id])
    vehicle = relationship("Vehicle", back_populates="trip", foreign_keys=[vehicle_id])
    issue = relationship("IssueLog", back_populates="trip")
    trip_start_location = relationship("TripSpecialLocation", foreign_keys=[trip_start_location_id], back_populates="start_trips")
    trip_end_location = relationship("TripSpecialLocation", foreign_keys=[trip_end_location_id], back_populates="end_trips")
    trip_stages = relationship("TripStage", back_populates="trip", cascade="all, delete-orphan")
    work_plans = relationship("WorkPlan", secondary=trip_workplan_association, back_populates="trips")
    employees = relationship("Employee", secondary=trip_employee_association, back_populates="trips")
    trip_report = relationship("TripReport", back_populates="trip", uselist=False)

    def __repr__(self):
        return f"<Trip(trip_code={self.trip_code}, status={self.status}, vehicle_id={self.vehicle_id}, driver_id={self.driver_id})>"


class TripStage(BaseTable):
    __tablename__ = "trip_stages"
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    mileage_at_arrival = Column(DECIMAL(10, 2), nullable=True)
    arrival_time = Column(DateTime, nullable=True)
    departure_time = Column(DateTime, nullable=True)
    stage_name = Column(String(255), nullable=False)
    trip = relationship("Trip", back_populates="trip_stages")
    site = relationship("Site", back_populates="trip_stages")


class TripReport(BaseTable):
    __tablename__ = "trip_reports"
    report_code = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), unique=True)
    workplan_id = Column(Integer, ForeignKey("work_plans.id"), nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
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
    __tablename__ = "issue_log_sources"
    name = Column(String(100), nullable=False, unique=True)
    issues = relationship("IssueLog", back_populates="source")


class IssueStatus(BaseTable):
    __tablename__ = "issue_statuses"
    status = Column(String(50), nullable=False, unique=True)
    issues = relationship("IssueLog", back_populates="status")


class IssueLog(BaseTable):
    __tablename__ = "issue_logs"
    issue = Column(Text, nullable=False)
    issue_description = Column(Text, nullable=True)
    key_recommendation = Column(Text, nullable=True)
    time_line_date = Column(Date, nullable=True)
    notes_on_closure = Column(Text, nullable=True)
    date_reported = Column(DateTime, default=datetime.datetime.utcnow)
    close_date = Column(DateTime, nullable=True)
    reported_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    thematic_area_id = Column(Integer, ForeignKey("thematic_areas.id"), nullable=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("issue_log_sources.id"))
    status_id = Column(Integer, ForeignKey("issue_statuses.id"))
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    srt_id = Column(Integer, ForeignKey("srts.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"), nullable=False)
    reported_by = relationship(
        "Employee", foreign_keys=[reported_by_id], back_populates="issue_logs_reported"
    )
    thematic_area = relationship("ThematicArea", back_populates="issues")
    site = relationship("Site", back_populates="issues")
    source = relationship("IssueLogSource", back_populates="issues")
    status = relationship("IssueStatus", back_populates="issues")
    meeting = relationship("Meeting", back_populates="issues")
    srt = relationship("SRT", back_populates="issues", foreign_keys=[srt_id])
    unit = relationship("Unit", back_populates="issues", foreign_keys=[unit_id])
    department = relationship(
        "Department", back_populates="issues", foreign_keys=[department_id]
    )
    tenancy = relationship("Tenancy", back_populates="issues")
    employees = relationship(
        "Employee", secondary=focal_person_issue_association, back_populates="issues"
    )
    trip = relationship("Trip", back_populates="issue")


class ActionPointSource(BaseTable):
    __tablename__ = "action_point_sources"
    name = Column(String(100), nullable=False, unique=True)
    action_points = relationship("ActionPoint", back_populates="source")


class ActionPoint(BaseTable):
    __tablename__ = "action_points"
    description = Column(Text, nullable=False)
    responsible_id = Column(Integer, ForeignKey("employees.id"))
    due_date = Column(Date)
    completion_date = Column(Date)
    status = Column(String(100))
    action_point_source_id = Column(Integer, ForeignKey("action_point_sources.id"))
    source = relationship("ActionPointSource", back_populates="action_points")
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    meeting = relationship("Meeting", back_populates="action_points")
    responsible = relationship(
        "Employee",
        foreign_keys=[responsible_id],
        back_populates="assigned_action_points",
    )


# Audit and Log Models
class AuditLog(BaseTable):
    __tablename__ = "audit_logs"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(SQLAEnum(ActionEnum), nullable=False)
    model = Column(String(50), nullable=False)
    model_id = Column(Integer, nullable=False)
    changes = Column(Text, nullable=True)
    user = relationship("User", back_populates="audit_logs")


# Human Resource Models

# Public Holiday Model
class PublicHoliday(BaseTable):
    __tablename__ = "public_holidays"
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    holiday_type_id = Column(Integer, ForeignKey("holiday_types.id"), nullable=True)
    holiday_type = relationship("HolidayType", back_populates="holidays")
    


# DocumentType Model
class DocumentType(BaseTable):
    __tablename__ = "document_types"
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    documents = relationship("Document", back_populates="document_type")

# Human Resource Models
class Document(BaseTable):
    __tablename__ = "documents"
    name = Column(String(255), nullable=False)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    document_type = relationship("DocumentType", back_populates="documents")
    file_path = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="documents")

class JobOpening(BaseTable):
    __tablename__ = "job_openings"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    status = Column(String(50), default="Open", nullable=False)
    applicants = relationship("Applicant", back_populates="job_opening")
    department = relationship("Department", back_populates="job_openings")


class Applicant(BaseTable):
    __tablename__ = "applicants"
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(50), nullable=False)
    resume_path = Column(String, nullable=False)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"), nullable=False)
    job_opening = relationship("JobOpening", back_populates="applicants")
    interviews = relationship("Interview", back_populates="applicant")

# class Timesheet(BaseTable):
#     __tablename__ = "timesheets"
#     employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
#     project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
#     date = Column(Date, nullable=False)
#     hours_worked = Column(DECIMAL(5, 2), nullable=False, default=8.5)
#     status = Column(String(50), nullable=False, default="Submitted")
#     created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     reviewed_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     approved_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     returned_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     archived_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
#     date_reviewed = Column(DateTime, nullable=True)
#     date_approved = Column(DateTime, nullable=True)
#     date_returned = Column(DateTime, nullable=True)
#     date_archived = Column(DateTime, nullable=True)
#     is_public_holiday = Column(Boolean, default=False)
#     is_leave = Column(Boolean, default=False)
#     return_reason = Column(Text, nullable=True)
#     comment = Column(Text, nullable=True)

#     # Relationships
#     employee = relationship("Employee", back_populates="timesheets", foreign_keys=[employee_id])
#     project = relationship("Project", back_populates="timesheets")
#     creator = relationship("Employee", foreign_keys=[created_by_id], back_populates="created_timesheets")
#     reviewer = relationship("Employee", foreign_keys=[reviewed_by_id], back_populates="reviewed_timesheets")
#     approver = relationship("Employee", foreign_keys=[approved_by_id], back_populates="approved_timesheets")
#     returned_by = relationship("Employee", foreign_keys=[returned_by_id], back_populates="returned_timesheets")
#     archived_by = relationship("Employee", foreign_keys=[archived_by_id], back_populates="archived_timesheets")

#     __table_args__ = (
#         CheckConstraint(
#             "hours_worked >= 0 AND hours_worked <= 24", name="check_hours_worked_valid"
#         ),
#         Index('ix_timesheet_date', 'date'),
#     )

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self._set_default_hours_worked()

#     def _set_default_hours_worked(self):
#         if not self.is_leave and not self.is_public_holiday:
#             weekday = self.date.weekday()
#             if weekday == 4:  # Friday
#                 self.hours_worked = 6.0
#             else:
#                 self.hours_worked = 8.5

class Timesheet(BaseTable):
    __tablename__ = "timesheets"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    date = Column(Date, nullable=False)
    hours_worked = Column(DECIMAL(5, 2), nullable=False, default=8.5)
    status = Column(String(50), nullable=False, default="Submitted")
    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    returned_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    archived_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    date_reviewed = Column(DateTime, nullable=True)
    date_approved = Column(DateTime, nullable=True)
    date_returned = Column(DateTime, nullable=True)
    date_archived = Column(DateTime, nullable=True)
    is_public_holiday = Column(Boolean, default=False)
    is_leave = Column(Boolean, default=False)
    return_reason = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)

    # Approval workflow fields
    approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
    current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)

    # Relationships for approval workflow
    approval_flow = relationship("ApprovalFlow", back_populates="timesheets")
    current_step = relationship("ApprovalStep")
    approval_logs = relationship("ApprovalLog", back_populates="timesheet")

    # Existing relationships
    employee = relationship("Employee", back_populates="timesheets", foreign_keys=[employee_id])
    project = relationship("Project", back_populates="timesheets")
    creator = relationship("Employee", foreign_keys=[created_by_id], back_populates="created_timesheets")
    reviewer = relationship("Employee", foreign_keys=[reviewed_by_id], back_populates="reviewed_timesheets")
    approver = relationship("Employee", foreign_keys=[approved_by_id], back_populates="approved_timesheets")
    returned_by = relationship("Employee", foreign_keys=[returned_by_id], back_populates="returned_timesheets")
    archived_by = relationship("Employee", foreign_keys=[archived_by_id], back_populates="archived_timesheets")

    __table_args__ = (
        CheckConstraint(
            "hours_worked >= 0 AND hours_worked <= 24", name="check_hours_worked_valid"
        ),
        Index('ix_timesheet_date', 'date'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_default_hours_worked()

    def _set_default_hours_worked(self):
        if not self.is_leave and not self.is_public_holiday:
            weekday = self.date.weekday()
            if weekday == 4:  # Friday
                self.hours_worked = 6.0
            else:
                self.hours_worked = 8.5

    def submit_for_approval(self):
        if not self.approval_flow:
            raise ValueError("An approval flow must be set before submission.")
        self.current_step = self.approval_flow.steps[0] if self.approval_flow.steps else None



class EmployeeType(BaseTable):
    __tablename__ = "employee_types"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    employees = relationship("Employee", back_populates="employee_type")

class HolidayType(BaseTable):
    __tablename__ = "holiday_types"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    holidays = relationship("PublicHoliday", back_populates="holiday_type")



class Employee(BaseTable):
    __tablename__ = "employees"
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_number = Column(String(25), unique=True, nullable=False)
    employee_type_id = Column(Integer, ForeignKey("employee_types.id"), nullable=True)
    staff_code = Column(String(100), unique=True, nullable=False)
    employee_email = Column(String(100), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    state_origin = Column(String(100), nullable=False)
    lga_origin = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    start_date =Column(Date, nullable=True)
    end_date =Column(Date, nullable=True)
    reason_for_leaving=Column(Text, nullable =True)
    gender = Column(String(20), nullable=True)
    signature = Column(String, nullable=True)  # Path to the employee's signature
    designation_id = Column(Integer, ForeignKey("designations.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    tenancy = relationship("Tenancy", back_populates="employees")
    designation = relationship("Designation", back_populates="employees")
    department = relationship("Department", back_populates="employees")
    employee_type = relationship("EmployeeType", back_populates="employees")
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
    documents = relationship("Document", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    payroll_records = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")
    salaries = relationship("Salary", back_populates="employee", cascade="all, delete-orphan")
    timesheets = relationship("Timesheet", back_populates="employee", foreign_keys="[Timesheet.employee_id]")
    created_timesheets = relationship("Timesheet", foreign_keys="[Timesheet.created_by_id]", back_populates="creator")
    reviewed_timesheets = relationship("Timesheet", foreign_keys="[Timesheet.reviewed_by_id]", back_populates="reviewer")
    approved_timesheets = relationship("Timesheet", foreign_keys="[Timesheet.approved_by_id]", back_populates="approver")
    returned_timesheets = relationship("Timesheet", foreign_keys="[Timesheet.returned_by_id]", back_populates="returned_by")
    archived_timesheets = relationship("Timesheet", foreign_keys="[Timesheet.archived_by_id]", back_populates="archived_by")
    # performance_reviews = relationship("PerformanceReview", foreign_keys="[PerformanceReview.employee_id]", back_populates="employee")
    # performance_reviews_given = relationship("PerformanceReview", foreign_keys="[PerformanceReview.reviewer_id]", back_populates="reviewer")
    
    # New Relationships for Personal Development Review
    personal_development_reviews = relationship(
        "PersonalDevelopmentReview",
        foreign_keys="[PersonalDevelopmentReview.employee_id]",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

    # This handles cases where the employee is the reviewer in a review
    reviews_given = relationship(
        "PersonalDevelopmentReview",
        foreign_keys="[PersonalDevelopmentReview.reviewer_id]",
        back_populates="reviewer"
    )
    trainings = relationship("Training", secondary=training_employee_association, back_populates="employees")
    bank_details = relationship("BankDetail", back_populates="employee", cascade="all, delete-orphan")
    meeting_minutes = relationship("MeetingMinutes", back_populates="employee")
    coordinated_meetings = relationship("Meeting", secondary=meeting_coordinator_association, back_populates="coordinators")
    moderated_meetings = relationship("Meeting", secondary=meeting_moderator_association, back_populates="moderators")
    interviews = relationship("Interview", secondary="interview_employee_association", back_populates="interviewers")
    projects = relationship("Project", secondary="project_employee_association", back_populates="employees")
    scopes_of_work = relationship("ScopeOfWork", secondary=scope_of_work_employee_association, back_populates="employees")
    line_items = relationship("ScopeOfWorkLineItem", secondary=scope_of_work_line_item_employee_association, back_populates="employees")
    subordinates = relationship("Employee", backref=backref("supervisor", remote_side="Employee.id"))
    trips = relationship("Trip", secondary=trip_employee_association, back_populates="employees")
    is_budget_holder = Column(Boolean, nullable=True)  # New field
    is_ceo = Column(Boolean, nullable=True)  # New field
    is_internal_auditor = Column(Boolean, nullable=True)  # New field for Internal Auditor
    is_compliance = Column(Boolean, nullable=True)  # New field for Compliance
    is_finance = Column(Boolean, nullable=True)  # New field for Finance
    is_hr = Column(Boolean, nullable=True)  # New field for HR



class Interview(BaseTable):
    __tablename__ = "interviews"
    date_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)
    feedback = Column(Text, nullable=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    applicant = relationship("Applicant", back_populates="interviews")
    interviewers = relationship(
        "Employee",
        secondary="interview_employee_association",
        back_populates="interviews",
    )


interview_employee_association = Table(
    "interview_employee_association",
    Base.metadata,
    Column("interview_id", Integer, ForeignKey("interviews.id"), primary_key=True),
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
)


# class PersonalDevelopmentReview(BaseTable):
#     __tablename__ = "personal_development_reviews"
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     review_period_start = Column(Date, nullable=False)
#     review_period_end = Column(Date, nullable=False)
#     comments = Column(Text, nullable=True)
#     employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
#     reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=False)  # Ensure this is defined
    
#     # Approval workflow fields
#     approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
#     current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)
    
#     # Relationships
#     employee = relationship("Employee", foreign_keys=[employee_id], back_populates="personal_development_reviews")
#     reviewer = relationship("Employee", foreign_keys=[reviewer_id], back_populates="reviews_given")  # Make sure this is correctly referenced
#     approval_flow = relationship("ApprovalFlow", back_populates="personal_development_reviews")
#     current_step = relationship("ApprovalStep")
#     approval_logs = relationship("ApprovalLog", back_populates="personal_development_review")

#     __table_args__ = (
#         CheckConstraint(
#             "review_period_end > review_period_start", name="check_review_period_valid"
#         ),
#     )


class PersonalDevelopmentReview(BaseTable):
    __tablename__ = "personal_development_reviews"
    
    # Fields specific to PersonalDevelopmentReview
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    comments = Column(Text, nullable=True)
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Approval workflow fields
    approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
    current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="personal_development_reviews")
    reviewer = relationship("Employee", foreign_keys=[reviewer_id], back_populates="reviews_given")
    approval_flow = relationship("ApprovalFlow", back_populates="personal_development_reviews")
    current_step = relationship("ApprovalStep")
    approval_logs = relationship("ApprovalLog", back_populates="personal_development_review")
    
    # Relationship with BroadBasedObjective
    broad_based_objectives = relationship("BroadBasedObjective", back_populates="review", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "review_period_end > review_period_start", name="check_review_period_valid"
        ),
    )


class BroadBasedObjective(BaseTable):
    __tablename__ = "broad_based_objectives"
    
    review_id = Column(Integer, ForeignKey("personal_development_reviews.id"), nullable=False)
    objective_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationship to PersonalDevelopmentReview
    review = relationship("PersonalDevelopmentReview", back_populates="broad_based_objectives")
    
    # Relationship with ResultBasedObjective
    result_based_objectives = relationship("ResultBasedObjective", back_populates="broad_based_objective", cascade="all, delete-orphan")


class ResultBasedObjective(BaseTable):
    __tablename__ = "result_based_objectives"
    
    broad_based_objective_id = Column(Integer, ForeignKey("broad_based_objectives.id"), nullable=False)
    objective_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    
    # Relationship to BroadBasedObjective
    broad_based_objective = relationship("BroadBasedObjective", back_populates="result_based_objectives")


# class PersonalDevelopmentReview(BaseTable):
#     __tablename__ = "personal_development_reviews"
    
#     # Fields specific to PersonalDevelopmentReview
#     review_period_start = Column(Date, nullable=False)
#     review_period_end = Column(Date, nullable=False)
#     comments = Column(Text, nullable=True)
    
#     # Fields for review content
#     goals = Column(Text, nullable=True)  # Assuming a single text field for multiple goals
#     strengths = Column(Text, nullable=True)
#     areas_for_improvement = Column(Text, nullable=True)
#     next_steps = Column(Text, nullable=True)
    
#     # Foreign keys and relationships
#     employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
#     reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=False)  # Assuming this is properly defined
    
#     # Approval workflow fields
#     approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
#     current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)
    
#     # Relationships
#     employee = relationship("Employee", foreign_keys=[employee_id], back_populates="personal_development_reviews")
#     reviewer = relationship("Employee", foreign_keys=[reviewer_id], back_populates="reviews_given")
#     approval_flow = relationship("ApprovalFlow", back_populates="personal_development_reviews")
#     current_step = relationship("ApprovalStep")
#     approval_logs = relationship("ApprovalLog", back_populates="personal_development_review")

#     __table_args__ = (
#         CheckConstraint(
#             "review_period_end > review_period_start", name="check_review_period_valid"
#         ),
#     )


class Training(BaseTable):
    __tablename__ = "trainings"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)
    employees = relationship(
        "Employee", secondary=training_employee_association, back_populates="trainings"
    )


# class LeaveRequest(BaseTable):
#     __tablename__ = "leave_requests"
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     status = Column(String(50), nullable=False)
#     reason = Column(Text, nullable=True)
#     hr_approval = Column(Boolean, default=False)
#     reliever_supervisor_approval = Column(Boolean, default=False)
#     finance_approval = Column(Boolean, default=False)
#     status = Column(String(50), default="Pending HR Approval")
#     employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
#     employee = relationship("Employee", back_populates="leave_requests")
#     __table_args__ = (
#         CheckConstraint(
#             "end_date > start_date", name="check_end_date_after_start_date"
#         ),
#     )

# Define LeaveType Model
class LeaveType(BaseTable):
    __tablename__ = "leave_types"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Establish relationship with LeaveRequest
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")

# # Update LeaveRequest Model
# class LeaveRequest(BaseTable):
#     __tablename__ = "leave_requests"

#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     status = Column(String(50), default="Pending HR Approval", nullable=False)
#     reason = Column(Text, nullable=True)
#     hr_approval = Column(Boolean, default=False)
#     reliever_supervisor_approval = Column(Boolean, default=False)
#     finance_approval = Column(Boolean, default=False)
    
#     # Foreign key to LeaveType
#     leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
#     leave_type = relationship("LeaveType", back_populates="leave_requests")
    
#     employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
#     employee = relationship("Employee", back_populates="leave_requests")

#     __table_args__ = (
#         CheckConstraint(
#             "end_date > start_date", name="check_end_date_after_start_date"
#         ),
#     )

class LeaveRequest(BaseTable):
    __tablename__ = "leave_requests"

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), default="Pending HR Approval", nullable=False)
    reason = Column(Text, nullable=True)
    hr_approval = Column(Boolean, default=False)
    reliever_supervisor_approval = Column(Boolean, default=False)
    finance_approval = Column(Boolean, default=False)
    
    # Foreign key to LeaveType
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="leave_requests")

    # Approval workflow fields
    approval_flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=True)
    current_step_id = Column(Integer, ForeignKey("approval_steps.id"), nullable=True)

    # Relationships for approval flow
    approval_flow = relationship("ApprovalFlow", back_populates="leave_requests")
    current_step = relationship("ApprovalStep")
    approval_logs = relationship("ApprovalLog", back_populates="leave_request")

    __table_args__ = (
        CheckConstraint(
            "end_date > start_date", name="check_end_date_after_start_date"
        ),
    )



class Attendance(BaseTable):
    __tablename__ = "attendance"
    date = Column(Date, nullable=False)
    clock_in_time = Column(Time, nullable=True)
    clock_out_time = Column(Time, nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="attendance_records")


class Payroll(BaseTable):
    __tablename__ = "payroll"
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    salary_id = Column(Integer, ForeignKey("salaries.id"), nullable=False)
    bonuses = Column(DECIMAL(10, 2), nullable=True)
    housing_allowance = Column(DECIMAL(10, 2), nullable=True)
    deductions = Column(DECIMAL(10, 2), nullable=True)
    net_pay = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    employee = relationship("Employee", back_populates="payroll_records")
    salary = relationship("Salary", back_populates="payrolls")


class Salary(BaseTable):
    __tablename__ = "salaries"
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    base_salary = Column(DECIMAL(10, 2), nullable=False)
    allowances = Column(DECIMAL(10, 2), nullable=True)
    effective_date = Column(Date, nullable=False)
    employee = relationship("Employee", back_populates="salaries")
    payrolls = relationship("Payroll", back_populates="salary")


class BankDetail(BaseTable):
    __tablename__ = "bank_details"
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    bank_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False, unique=True)
    ifsc_code = Column(String(20), nullable=True)
    employee = relationship("Employee", back_populates="bank_details")


# Project Models
class Funder(BaseTable):
    __tablename__ = "funders"
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    projects = relationship("Project", secondary="funding", back_populates="funders")
    funding = relationship("Funding", back_populates="funder")


class Project(BaseTable):
    __tablename__ = "projects"
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    project_sum = Column(DECIMAL(15, 2), nullable=False)
    funders = relationship("Funder", secondary="funding", back_populates="projects")
    components = relationship("ProjectComponent", back_populates="project")
    tenancies = relationship(
        "Tenancy", secondary=project_tenancy_association, back_populates="projects"
    )
    employees = relationship(
        "Employee", secondary=project_employee_association, back_populates="projects"
    )
    timesheets = relationship("TimeSheet", back_populates="project")
    funding = relationship("Funding", back_populates="project")
    work_plans = relationship("WorkPlan", back_populates="project")
    timesheets = relationship("Timesheet", back_populates="project")

class ProjectComponent(BaseTable):
    __tablename__ = "project_components"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="components")
    funding = relationship("Funding", back_populates="component")

class Funding(BaseTable):
    __tablename__ = "funding"
    __table_args__ = {"extend_existing": True}
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    funder_id = Column(Integer, ForeignKey("funders.id"), primary_key=True)
    component_id = Column(
        Integer, ForeignKey("project_components.id"), primary_key=True
    )
    amount_funded = Column(DECIMAL(15, 2), nullable=False)
    project = relationship("Project", back_populates="funding")
    funder = relationship("Funder", back_populates="funding")
    component = relationship("ProjectComponent", back_populates="funding")


class TripSpecialLocation(BaseTable):
    __tablename__ = "trip_special_locations"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(DECIMAL(9, 6), nullable=True)
    longitude = Column(DECIMAL(9, 6), nullable=True)
    tenancy_id = Column(Integer, ForeignKey("tenancy.id"))
    tenancy = relationship("Tenancy", back_populates="special_locations")
    
    start_trips = relationship("Trip", foreign_keys="[Trip.trip_start_location_id]", back_populates="trip_start_location")
    end_trips = relationship("Trip", foreign_keys="[Trip.trip_end_location_id]", back_populates="trip_end_location")

# Call configure_mappers() after defining all models
configure_mappers()