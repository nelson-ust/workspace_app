


from datetime import datetime
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Path, Query, UploadFile,status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.dependencies import role_checker
from auth.security import get_current_user
from schemas.user_schemas import UserRead
from schemas.trip_report_schemas import IssueDetail, TripReportSchema, TripReportSubmission
from db.database import get_db
from repositories.trip_report_repository import TripReportRepository
from logging_helpers import logging_helper, ActionEnum

router = APIRouter()



# @router.post("/trip-reports/submit", status_code=status.HTTP_201_CREATED)
# async def submit_trip_report(
#     background_tasks: BackgroundTasks,
#     submission: TripReportSubmission = Body(...),
#     document: UploadFile = File(None),
#     current_user: UserRead = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     _: UserRead = Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team", "hq_lead"]))
# ):
#     if submission.trip_completed and document is None:
#         raise HTTPException(status_code=400, detail="Document is required when the trip is completed.")
#     if not submission.trip_completed and document is not None:
#         raise HTTPException(status_code=400, detail="Document should not be uploaded when the trip is not completed.")
    
#     try:
#         logging_helper.log_info("Accessing - Submit Trip Report - Endpoint")

#         trip_report_repo = TripReportRepository(db)
#         result = trip_report_repo.submit_trip_report(
#             trip_id=submission.trip_id,
#             workplan_id=submission.workplan_id,
#             document=document,
#             summary=submission.summary,
#             trip_outcome=submission.trip_outcome,
#             observations=submission.observations,
#             issue_identified=submission.issue_identified,
#             trip_completed=submission.trip_completed,
#             reason=submission.reason,
#             site_ids=submission.site_ids,
#             issues=submission.issues
#         )
#         changes = submission.dict()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.SUBMIT_TRIP_REPORT, "TripReport", submission.trip_id, changes)
#         return result
#     except HTTPException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception as e:
#         logging_helper.log_error(f"Exception: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/trip-reports/submit", status_code=201)
def submit_trip_report(
    trip_id: int = Query(...),
    workplan_id: int = Query(...),
    summary: Optional[str] = Query(None),
    trip_outcome: Optional[str] = Query(None),
    observations: Optional[str] = Query(None),
    issue_identified: Optional[bool] = Query(None),
    trip_completed: Optional[bool] = Query(None, description="Indicates if the trip was completed"),
    reason: Optional[str] = Query(None),
    issue_description: Optional[str] = Query(None),
    site_ids: Optional[List[int]] = Query(None),
    status_id: Optional[int] = Query(None),
    time_line_date: Optional[datetime] = Query(None),
    key_recommendation: Optional[str] = Query(None),
    focal_persons: Optional[List[int]] = Query(None),  # Updated to accept a list of focal persons
    #document: Optional[UploadFile] = File(None),  # Make document optional
    document: UploadFile=File,
    db: Session = Depends(get_db),
    _ = Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team", "hq_lead"])),
    current_user: UserRead = Depends(get_current_user)
):
    if trip_completed and document is None:
        raise HTTPException(status_code=400, detail="Document is required when the trip is completed.")
    if not trip_completed and document is not None:
        raise HTTPException(status_code=400, detail="Document should not be uploaded when the trip is not completed.")
    
    logging_helper.log_info("Accessing - Submit Trip Report - Endpoint")
    try:
        trip_report_repo = TripReportRepository(db)
        result = trip_report_repo.submit_trip_report(
            trip_id=trip_id,
            workplan_id=workplan_id,
            document=document,
            summary=summary,
            trip_outcome=trip_outcome,
            observations=observations,
            issue_identified=issue_identified,
            trip_completed=trip_completed,
            reason=reason,
            issue_description=issue_description,
            site_ids=site_ids,
            status_id=status_id,
            time_line_date=time_line_date,
            key_recommendation=key_recommendation,
            focal_persons=focal_persons  # Pass the list of focal persons
        )
        changes = {
            "trip_id": trip_id,
            "workplan_id": workplan_id,
            "summary": summary,
            "trip_outcome": trip_outcome,
            "observations": observations,
            "issue_identified": issue_identified,
            "trip_completed": trip_completed,
            "reason": reason,
            "issue_description": issue_description,
            "site_ids": site_ids,
            "status_id": status_id,
            "time_line_date": time_line_date,
            "key_recommendation": key_recommendation,
            "focal_persons": focal_persons  # Include focal persons in changes
        }
        logging_helper.log_audit(db, current_user.id, ActionEnum.SUBMIT_TRIP_REPORT, "TripReport", trip_id, changes)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trip-reports/{trip_report_id}")
def fetch_trip_report(trip_report_id: int = Path(..., description="The ID of the trip report to retrieve"), db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    """
    Retrieves a trip report by its ID.
    """
    logging_helper.log_info("Accessing - Fetch Trip Report - Endpoint")
    repository = TripReportRepository(db)
    try:
        trip_report = repository.get_trip_report_by_id(trip_report_id)
        return trip_report
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    

@router.get("/trip-reports", response_model=List[dict])
def fetch_all_trip_reports(db: Session = Depends(get_db),_ = Depends(role_checker(["super_admin", "unit_member", "tenant_admin", "program_team"])), current_user: UserRead = Depends(get_current_user)):
    """
    Fetches all trip reports from the database along with detailed work plan and employee information.
    """
    logging_helper.log_info("Accessing - Fetch all Trip Reports - Endpoint")
    try:
        repository = TripReportRepository(db)
        return repository.get_all_trip_reports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-trip-report/{workplan_id}", response_class=FileResponse)
async def download_trip_report(workplan_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    """
    Downloads the Trip report uploaded based on the Trip Report ID and associated WorkPlan ID.
    """
    logging_helper.log_info("Accessing - Download Trip Report - Endpoint")
    repository = TripReportRepository(db)
    try:
        file_path = repository.get_trip_report_file_path(workplan_id)
        changes = {'message': f'Downloaded trip report for workplan: {workplan_id}'}
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "TripReport", workplan_id, changes)
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_path.split('/')[-1])
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/trips/completed-without-reports", response_model=List[Dict])
def get_completed_trips_without_reports(
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
    tenancy_id: Optional[int] = Query(None, description="Optional tenancy ID to filter the results"),
     _ = Depends(role_checker(['chief_driver', 'admin_lead', 'tenant_admin', 'super_admin']))
):
    logging_helper.log_info(f"Accessing - Get Completed Trips without Reports - Endpoint with tenancy_id={tenancy_id}")
    try:
        trip_report_repo = TripReportRepository(db)
        result = trip_report_repo.get_completed_trips_without_reports(tenancy_id)
        logging_helper.log_info("Successfully retrieved completed trips without trip reports")
        return result
    except HTTPException as e:
        logging_helper.log_error(f"HTTPException: {str(e.detail)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logging_helper.log_error(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/trips-without-reports", response_model=List[Dict])
def get_trips_without_reports(
    current_user: UserRead = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Endpoint to get details of trips without a submitted report.
    """
    try:
        trip_report_repo = TripReportRepository(db)
        details = trip_report_repo.get_trips_without_reports_details(tenancy_id=current_user.tenancy_id)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))