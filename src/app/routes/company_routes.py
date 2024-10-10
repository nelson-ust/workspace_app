# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from sqlalchemy.orm import Session
# from typing import List
# from db.database import get_db
# from repositories.company_repository import CompanyRepository
# from logging_helpers import logging_helper
# from auth.security import get_current_user
# from models.all_models import User, ActionEnum
# from schemas.company_schemas import CompanyCreate, CompanyUpdate, CompanyResponse, ThirdPartyParticipantCreate
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# import json

# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter()

# @router.post("/companies/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def create_company(request: Request, company: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     logging_helper.log_info("Accessing - Create Company - Endpoint")
#     company_repo = CompanyRepository(db)
#     try:
#         new_company = company_repo.create_company(company)
#         logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Company", new_company.id, json.dumps(new_company, default=str))
#         return CompanyResponse.from_orm(new_company)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to create company: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create company")


# @router.get("/companies/{company_id}", status_code=status.HTTP_200_OK, response_model=CompanyResponse)
# @limiter.limit("10/minute")
# async def read_company(request: Request, company_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Read Company - Endpoint")
#     company_repo = CompanyRepository(db)
#     try:
#         company = company_repo.get_company_by_id(company_id)
#         if not company:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Company", company_id, None)
#         return CompanyResponse.from_orm(company)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch company: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch company")

# @router.get("/companies/", status_code=status.HTTP_200_OK, response_model=List[CompanyResponse])
# @limiter.limit("10/minute")
# async def read_companies(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Read All Companies - Endpoint")
#     company_repo = CompanyRepository(db)
#     try:
#         companies = company_repo.get_all_companies()
#         logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Company", None, "Read all companies")
#         return [CompanyResponse.from_orm(company) for company in companies]
#     except Exception as e:
#         logging_helper.log_error(f"Failed to fetch companies: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch companies")

# @router.put("/companies/{company_id}", status_code=status.HTTP_200_OK, response_model=CompanyResponse)
# @limiter.limit("5/minute")
# async def update_company(request: Request, company_id: int, company: CompanyUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Update Company - Endpoint")
#     company_repo = CompanyRepository(db)
#     try:
#         updated_company = company_repo.update_company(company_id, name=company.name)
#         if not updated_company:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
#         logging_helper.log_audit(
#             db, current_user.id, ActionEnum.UPDATE, "Company", company_id, json.dumps(updated_company, default=str)
#         )
#         return CompanyResponse.from_orm(updated_company)
#     except Exception as e:
#         logging_helper.log_error(f"Failed to update company: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update company")

# @router.delete("/companies/{company_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def delete_company(request: Request, company_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info("Accessing - Delete Company - Endpoint")
#     company_repo = CompanyRepository(db)
#     try:
#         deleted_company = company_repo.delete_company(company_id)
#         if not deleted_company:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
#         logging_helper.log_audit(
#             db, current_user.id, ActionEnum.DELETE, "Company", company_id, json.dumps(deleted_company, default=str)
#         )
#         return {"message": f"The Company with ID: {company_id} deleted successfully!"}
#     except Exception as e:
#         logging_helper.log_error(f"Failed to delete company: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete company")


# @router.post("/companies/{company_id}/participants", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute")
# async def add_third_party_participant(request: Request, company_id: int, participant: ThirdPartyParticipantCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     logging_helper.log_info(f"Accessing - Add Third Party Participant - Endpoint for company ID: {company_id}")
#     company_repo = CompanyRepository(db)
#     try:
#         new_participant = company_repo.add_third_party_participant(
#             company_id=company_id,
#             name=participant.name,
#             email=participant.email,
#             phone_number=participant.phone_number,
#             site_id=participant.site_id
#         )
#         logging_helper.log_audit(
#             db, current_user.id, ActionEnum.CREATE, "ThirdPartyParticipant", new_participant.id, json.dumps(new_participant, default=str)
#         )
#         return new_participant
#     except Exception as e:
#         logging_helper.log_error(f"Failed to add third-party participant: {str(e)}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add third-party participant")



from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from repositories.company_repository import CompanyRepository
from logging_helpers import logging_helper
from auth.security import get_current_user
from models.all_models import User, ActionEnum
from schemas.company_schemas import CompanyCreate, CompanyUpdate, CompanyResponse, ThirdPartyParticipantCreate
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/companies/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_company(request: Request, company: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new company.

    Args:
        request (Request): The request object.
        company (CompanyCreate): The data for the new company.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        CompanyResponse: The newly created company object.

    Roles to Access the endpoint
        super_admin, tenant_admin, Program_lead
    """
    logging_helper.log_info("Accessing - Create Company - Endpoint")
    company_repo = CompanyRepository(db)
    try:
        new_company = company_repo.create_company(company)
        logging_helper.log_audit(db, current_user.id, ActionEnum.CREATE, "Company", new_company.id, json.dumps(new_company, default=str))
        return CompanyResponse.from_orm(new_company)
    except Exception as e:
        logging_helper.log_error(f"Failed to create company: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create company")


@router.get("/companies/{company_id}", status_code=status.HTTP_200_OK, response_model=CompanyResponse)
@limiter.limit("10/minute")
async def read_company(request: Request, company_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve a company by its ID.

    Args:
        request (Request): The request object.
        company_id (int): The ID of the company to retrieve.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        CompanyResponse: The company object if found.

    Roles to Access the endpoint
        super_admin, tenant_admin, Program_lead, Program_team 
    """
    logging_helper.log_info("Accessing - Read Company - Endpoint")
    company_repo = CompanyRepository(db)
    try:
        company = company_repo.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Company", company_id, None)
        return CompanyResponse.from_orm(company)
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch company: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch company")

@router.get("/companies/", status_code=status.HTTP_200_OK, response_model=List[CompanyResponse])
@limiter.limit("10/minute")
async def read_companies(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve all companies.

    Args:
        request (Request): The request object.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        List[CompanyResponse]: A list of all company objects.

    Roles to Access the endpoint
        super_admin, tenant_admin, Program_lead, Program_team
    """
    logging_helper.log_info("Accessing - Read All Companies - Endpoint")
    company_repo = CompanyRepository(db)
    try:
        companies = company_repo.get_all_companies()
        logging_helper.log_audit(db, current_user.id, ActionEnum.READ, "Company", None, "Read all companies")
        return [CompanyResponse.from_orm(company) for company in companies]
    except Exception as e:
        logging_helper.log_error(f"Failed to fetch companies: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch companies")

@router.put("/companies/{company_id}", status_code=status.HTTP_200_OK, response_model=CompanyResponse)
@limiter.limit("5/minute")
async def update_company(request: Request, company_id: int, company: CompanyUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update a company's details.

    Args:
        request (Request): The request object.
        company_id (int): The ID of the company to update.
        company (CompanyUpdate): The new data for the company.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        CompanyResponse: The updated company object if found.

    Roles to Access the endpoint
        super_admin, tenant_admin, Program_lead, Program_team
    """
    logging_helper.log_info("Accessing - Update Company - Endpoint")
    company_repo = CompanyRepository(db)
    try:
        updated_company = company_repo.update_company(company_id, name=company.name)
        if not updated_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.UPDATE, "Company", company_id, json.dumps(updated_company, default=str)
        )
        return CompanyResponse.from_orm(updated_company)
    except Exception as e:
        logging_helper.log_error(f"Failed to update company: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update company")

@router.delete("/companies/{company_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_company(request: Request, company_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete a company by its ID.

    Args:
        request (Request): The request object.
        company_id (int): The ID of the company to delete.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Dict[str, str]: A message confirming the deletion.

    Roles to Access the endpoint
        super_admin, tenant_admin
    """
    logging_helper.log_info("Accessing - Delete Company - Endpoint")
    company_repo = CompanyRepository(db)
    try:
        deleted_company = company_repo.delete_company(company_id)
        if not deleted_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.DELETE, "Company", company_id, json.dumps(deleted_company, default=str)
        )
        return {"message": f"The Company with ID: {company_id} deleted successfully!"}
    except Exception as e:
        logging_helper.log_error(f"Failed to delete company: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete company")


@router.post("/companies/{company_id}/participants", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_third_party_participant(request: Request, company_id: int, participant: ThirdPartyParticipantCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Add a third-party participant to a company.

    Args:
        request (Request): The request object.
        company_id (int): The ID of the company.
        participant (ThirdPartyParticipantCreate): The data for the new participant.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        ThirdPartyParticipant: The newly created participant object.

    Roles to Access the endpoint
        super_admin, tenant_admin, Program_lead, Program_team
    """
    logging_helper.log_info(f"Accessing - Add Third Party Participant - Endpoint for company ID: {company_id}")
    company_repo = CompanyRepository(db)
    try:
        new_participant = company_repo.add_third_party_participant(
            company_id=company_id,
            name=participant.name,
            email=participant.email,
            phone_number=participant.phone_number,
            site_id=participant.site_id
        )
        logging_helper.log_audit(
            db, current_user.id, ActionEnum.CREATE, "ThirdPartyParticipant", new_participant.id, json.dumps(new_participant, default=str)
        )
        return new_participant
    except Exception as e:
        logging_helper.log_error(f"Failed to add third-party participant: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add third-party participant")
