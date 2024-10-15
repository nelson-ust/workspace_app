from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import get_db
from routes.unit_routes import router as unit_router
from routes.department_routes import router as dept_router
from routes.tenancy_routes import router as tenancy_router
from routes.userRole_routes import router as user_role_router
from routes.user_routes import router as user_router
from routes.auth_routes import router as auth_router
from routes.srt_routes import router as srt_router
from routes.employee_routes import router as employee_router
from routes.location_routes import router as location_router
from routes.workplanSource_routes import router as workplansource_router
from routes.designation_routes import router as designation_router
from routes.actionPointSource_route import router as action_point_source_router
from routes.issueLogSource_routes import router as issue_log_source_router
from routes.maintenanceType_routes import router as vehicle_maintenance_type_router
from routes.workplan_routes import router as work_plan_router
from routes.thematic_area_routes import router as thematic_area_router
from routes.driver_routes import router as driver_router
from routes.fuel_purchase_routes import router as fuel_purchase_router
from routes.vehicle_routes import router as vehicle_router
from routes.vehicle_maintenance_routes import router as vehicle_maintenance_router
from routes.trip_routes import router as trip_router
from routes.site_routes import router as site_router
from routes.trip_report_routes import router as trip_report_router
from routes.issue_status_routes import router as issue_status_router
from routes.custom_query_router import router as custom_query_router
from routes.audit_log_routes import router as audit_log_router
from routes.login_history_routes import router as login_history_router
from routes.task_status_routes import router as task_status_router
from routes.assignment_routes import router as assignment_router
from routes.task_routes import router as task_router
from routes.issue_routes import router as issue_router
from routes.milestone_routes import router as milestone_router
from routes.company_routes import router as company_router
from routes.meeting_routes import router as meeting_router
from routes.third_party_participant_routes import router as third_party_participant_router
from routes.meeting_type_routes import router as meeting_type_router
from routes.meal_combination_routes import router as meal_combination_router
from routes.funder_routes import router as funder_router
from routes.funding_routes import router as funding_router
from routes.project_routes import router as project_router
from routes.project_component_routes import router as project_component_router
from routes.trip_special_location_routes import router as trip_special_location_router
from routes.document_type_routes import router as document_type_router
from routes.document_routes import router as document_router
from routes.bank_details_routes import router as bank_details_router
from routes.holiday_routes import router as holiday_router
from routes.leave_request_routes import router as leave_request_router
from routes.leave_request_type_routes import  router as leave_request_type_router
from routes.public_holiday_type_routes import router as public_holiday_type_router
from routes.employee_type_routes import router as employee_type_router
from routes.whatsapp_integrator_route import router as whatsapp_router 
from routes.approval_flow_routes import router as approval_flow_router
from routes.approval_step_routes import router as approval_step_router
from routes.personal_development_performance_review_routes import router as pdp_router
from routes.module_routes import router as module_router
from routes.route_management_routes import router as route_management_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.openapi.utils import get_openapi
import uvicorn
from logging_config import logger
from apscheduler.schedulers.background import BackgroundScheduler
from auth.email import send_birthday_emails, send_log_files_email

# Configure logging
logger.info("Starting the WorkPlan Management System application...")

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the scheduler
    scheduler = BackgroundScheduler()

    def send_birthday_emails_wrapper():
        """Wrapper function to provide the database session."""
        db_session = next(get_db())
        try:
            send_birthday_emails(db_session)
        finally:
            db_session.close()

    # Add the scheduled jobs
    scheduler.add_job(send_log_files_email, 'cron', day_of_week='sun', hour=23, minute=19)
    scheduler.add_job(send_birthday_emails_wrapper, 'cron', hour=18, minute=27)
    
    scheduler.start()
    logger.info("Scheduler started...")
    
    yield
    
    scheduler.shutdown()
    logger.info("Scheduler shut down...")

app = FastAPI(
    title="WorkPlan Management System",
    version="1.0.0",
    description="API for managing WorkPlan Across CCFN supported states and the FCT",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify domains for production
    allow_credentials=True,
    allow_methods=["*"],  # You might want to restrict to ["GET", "POST", "PUT", "DELETE"] etc.
    allow_headers=["*"],
)

# Adding the rate limit exceeded exception handler to the FastAPI app
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", tags=["Root"])
async def read_root():
    # Dynamically return app details including its version
    logger.info("Root endpoint accessed.")
    return {
        "message": "Welcome to the Workspace Management API!",
        "app_name": app.title,
        "version": app.version,
        "description": app.description,
    }

# Include your routers
app.include_router(route_management_router, prefix="/api/v1", tags=["Route Management"])
app.include_router(funder_router,prefix="/api/v1",tags=["Funder"])
app.include_router(project_router,prefix="/api/v1",tags=["Projects"])
app.include_router(approval_step_router, prefix="/api/v1", tags=["Approval Steps"])
app.include_router(approval_flow_router,prefix="/api/v1", tags=["Approval Flow"])
app.include_router(pdp_router,prefix="/api/v1", tags=["PDP"])
app.include_router(module_router, prefix="/api/v1", tags=["Module"])
app.include_router(project_component_router,prefix="/api/v1",tags=["Project Components"])
app.include_router(funding_router,prefix="/api/v1",tags=["Funding"])
app.include_router(tenancy_router, prefix="/api/v1", tags=["Tenancy"])
app.include_router(user_role_router, prefix="/api/v1", tags=["UserRole"])
app.include_router(designation_router, prefix="/api/v1", tags=["Designation"])
app.include_router(dept_router, prefix="/api/v1", tags=["Department"])
app.include_router(unit_router, prefix="/api/v1", tags=["Units"])
app.include_router(srt_router, prefix="/api/v1", tags=["SRT"])
app.include_router(workplansource_router, prefix="/api/v1", tags=["WorkPlan Sources"])
app.include_router(location_router, prefix="/api/v1", tags=["Location"])
app.include_router(site_router, prefix="/api/v1", tags=["Site"])
app.include_router(action_point_source_router, prefix="/api/v1", tags=["Action Point Sources"])
app.include_router(issue_log_source_router, prefix="/api/v1", tags=["IssueLog Sources"])
app.include_router(vehicle_maintenance_type_router, prefix="/api/v1", tags=["Vehicle Maintenance Types"])
app.include_router(work_plan_router, prefix="/api/v1", tags=["Work Plans"])
app.include_router(trip_router, prefix="/api/v1", tags=["Trips"])
#app.include_router(trip_start_location_router, prefix="/api/v1", tags=["Trip Start Location"])
app.include_router(trip_special_location_router, prefix="/api/v1/trip-special-locations",tags=["trip-special-locations"])

app.include_router(trip_report_router, prefix="/api/v1", tags=["Trip Reports"])
app.include_router(thematic_area_router, prefix="/api/v1", tags=["Thematic Areas"])
app.include_router(public_holiday_type_router, prefix="/api/v1", tags=["Public Holiday Types"])
app.include_router(employee_type_router, prefix="/api/v1", tags=["Employee Types"])
app.include_router(employee_router, prefix="/api/v1", tags=["Employees"])
app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(driver_router, prefix="/api/v1", tags=["Drivers"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(vehicle_router, prefix="/api/v1", tags=["Vehicles"])
app.include_router(vehicle_maintenance_router, prefix="/api/v1", tags=["Vehicle Maintenance"])
app.include_router(fuel_purchase_router, prefix="/api/v1", tags=["Fuel Purchases"])
app.include_router(issue_status_router, prefix="/api/v1", tags=["Issue Status"])
app.include_router(custom_query_router, prefix="/api/v1", tags=["Custom Query"])
app.include_router(audit_log_router, prefix="/api/v1", tags=["Audit Trail"])
app.include_router(login_history_router, prefix="/api/v1", tags=["Login History"])
app.include_router(task_status_router, prefix="/api/v1", tags=["Task Status"])
app.include_router(assignment_router, prefix="/api/v1", tags=["Assignment"])
app.include_router(milestone_router, prefix="/api/v1", tags=["Milestone"])
app.include_router(task_router, prefix="/api/v1", tags=["Task"])
app.include_router(issue_router,prefix="/api/v1", tags=["Issue"])
app.include_router(company_router,prefix="/api/v1", tags=["Company"])
app.include_router(meeting_router,prefix="/api/v1", tags=["Meeting"])
app.include_router(third_party_participant_router,prefix="/api/v1", tags=["Third_Party_Participant"])
app.include_router(meeting_type_router,prefix="/api/v1", tags=["Meeting Type"])
app.include_router(meal_combination_router,prefix="/api/v1", tags=["Meal Combination"])
app.include_router(document_type_router,prefix="/api/v1", tags=["employee-document-types"])
app.include_router(document_router, prefix="/api/v1", tags=["employee-documents"])
app.include_router(bank_details_router, prefix="/app/v1", tags=["employee-bank-details"])
app.include_router(holiday_router, prefix="/api/v1", tags=["public-holidays"])
app.include_router(leave_request_router,prefix="/api/v1",tags=["leave-request"])
app.include_router(leave_request_type_router,prefix="/api/v1", tags=["leave-request-type"])
app.include_router(whatsapp_router, prefix="/api/v1", tags=["WhatsApp Integration"])
#
# app.include_router(meeting_router,prefix="/api/v1", tags=["Meeting"]) Define OAuth2 configuration
oauth2_scheme = {
    "type": "oauth2",
    "flows": {"password": {"tokenUrl": "/api/v1/login", "scopes": {}}},
}

def custom_openapi():
    logger.debug("Generating custom OpenAPI schema")
    if app.openapi_schema:
        logger.debug("Returning cached schema")
        return app.openapi_schema
    try:
        openapi_schema = get_openapi(
            title="CCFN Workspace Management App",
            version="1.0",
            description="Detailed description of your API.",
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/login",
                        "scopes": {}
                    }
                }
            }
        }
        app.openapi_schema = openapi_schema
        logger.debug("Schema generated successfully")
    except Exception as e:
        logger.error(f"Failed to generate schema: {str(e)}", exc_info=True)
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


