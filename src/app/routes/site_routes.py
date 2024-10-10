from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.database import get_db
from repositories.site_repository import SiteRepository
from schemas.site_schemas import SiteCreate, SiteUpdate, SiteRead
from schemas.user_schemas import UserRead
from auth.security import get_current_user
from auth.dependencies import role_checker 
from logging_helpers import logging_helper

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/site/", response_model= SiteRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def create_site(request:Request, site_data:SiteCreate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Create Site - Endpoint")
    site_repo = SiteRepository(db)
    
    try:
        #super_admin check
        for role_dict in current_user.roles:
            if role_dict.name == "super_admin" or current_user.tenancy_id == site_data.tenancy_id:
                new_site = site_repo.create_site(site_data=site_data)
                break
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{current_user.first_name} {current_user.last_name}, your authorized to create site for only your state")
        return new_site
    except Exception as e:
        logging_helper.log_error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error creating unit: Warning Unauthorized: {str(e)}")


@router.get("/site/", response_model= List[SiteRead], status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_all_sites(request:Request, skip:int=0, limit:int=100, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get all Sites - Endpoint")
    site_repo = SiteRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                return site_repo.get_all_sites(skip=skip, limit=limit)
            else:
                return site_repo.get_all_sites(tenancy_id=current_user.tenancy_id, skip=skip, limit=limit)
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.get("/site/{site_id}/", response_model= SiteRead, status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_sites_by_id(request:Request, site_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get Sites by id - Endpoint")
    site_repo = SiteRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                site = site_repo.get_sites_by_id(site_id=site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with id {site_id} is not found")
                return site
            else:
                site = site_repo.get_sites_by_id(site_id=site_id, tenancy_id=current_user.tenancy_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with id {site_id} is not found")
                return site
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.get("/site/{site_name}/site_name", response_model= List[SiteRead], status_code=status.HTTP_201_CREATED) 
@limiter.limit("5/minute")
async def get_site_by_name(request:Request, site_name:str, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['unit_member','programs_lead','technical_lead', 'stl', 'hq_backstop', 'tenant_admin','super_admin']))):
    
    logging_helper.log_info("Accessing - Get Site by Name - Endpoint")
    site_repo = SiteRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_backstop"]:
                site = site_repo.get_site_by_name(site_name=site_name)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with name {site_name} is not found")
                return site
            else:
                site = site_repo.get_site_by_name(site_name=site_name, tenancy_id=current_user.tenancy_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with name {site_name} is not found")
                return site
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.put("/site/{site_id}/update_site") 
@limiter.limit("5/minute")
async def update_site(request:Request, site_id:int, site_data:SiteUpdate, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['tenant_admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Update Site - Endpoint")
    site_repo = SiteRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin", "hq_staff"]:
                site = site_repo.update_site(site_id=site_id, site_data=site_data)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with name {site_data.name} is not found")
                return site
            else:
                site = site_repo.update_site(site_id=site_id, site_data=site_data, tenancy_id=current_user.tenancy_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with name {site_data.name} is not found")
                return site
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.delete("/site/{site_id}/soft_delete_sites") 
@limiter.limit("5/minute")
async def soft_delete_sites(request:Request, site_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['tenant_admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Soft Delete Sites - Endpoint")
    site_repo = SiteRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                site = site_repo.soft_delete_sites(site_id=site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with ID {site_id} is not found")
                return site
            else:
                site = site_repo.soft_delete_sites(site_id=site_id, tenancy_id=current_user.tenancy_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with ID {site_id} is not found")
                return site
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


@router.post("/site/{site_id}/restore_site") 
@limiter.limit("5/minute")
async def restore_site(request:Request, site_id:int, current_user:UserRead=Depends(get_current_user), 
                         db: Session = Depends(get_db),_=Depends(role_checker(['tenant_admin', 'super_admin']))):
    
    logging_helper.log_info("Accessing - Restore Site - Endpoint")
    site_repo = SiteRepository(db)
    try:
        for role_dict in current_user.roles:
            if role_dict.name in ["super_admin"]:
                site = site_repo.restore_site(site_id=site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with ID {site_id} is not found")
                return site
            else:
                site = site_repo.restore_site(site_id=site_id, tenancy_id=current_user.tenancy_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Site with ID {site_id} is not found")
                return site
    except Exception as err:
        logging_helper.log_error(f"{str(err)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(err)}")


