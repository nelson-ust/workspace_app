# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy import or_
# from schemas.site_schemas import SiteCreate, SiteUpdate
# from models.all_models import Site, Tenancy, Location
# from repositories.base_repository import BaseRepository
# from sqlalchemy.exc import SQLAlchemyError
# from typing import Optional, List, Type
# import logging
# from datetime import date, datetime



# class SiteRepository(BaseRepository[Site, SiteCreate, SiteUpdate]):
#     def __init__(self, db_session: Session):
#         super().__init__(Site, db_session)


#     def create_site(self, site_data: SiteCreate) -> Site:
#         """
#         Creates a new Site ensuring that the site is unique within the Site table and Tenenant.
#         """
#         site_existence = (
#             self.db_session.query(Site)
#             .filter(Site.name == site_data.name, Site.tenancy_id == site_data.tenancy_id)
#             .first()
#         )
#         if site_existence:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Site with the name {site_data.name} already exists in this State with tenacncy_id {site_data.tenancy_id} !!!",
#             )
#         #check for location existence in the tenant
#         location_existence = self.db_session.query(Location).filter(Location.id == site_data.location_id, Location.tenancy_id==site_data.tenancy_id).first()
#         if not location_existence:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Kindly ensure the location ID {site_data.location_id} supplied to the new site is for the state")

#         try:
#             return self.create(site_data)
#         except Exception as err:
#             self.handle_errors(
#                 e=err, message=f"Database Error during Site creation {err}"
#             )


#     def get_all_sites(self, skip:int=0, limit:int=100, tenancy_id:Optional[int]=None) -> List[Site]:
#         """
#         Retrieves all Sites that are active with optional pagination.
#         """
#         try:
#             if tenancy_id:
#                 sites = self.db_session.query(Site).filter(Site.is_active==True, Site.tenancy_id==tenancy_id).offset(offset=skip).limit(limit=limit).all()
#                 return sites
#             else:
#                 sites = self.db_session.query(Site).filter(Site.is_active==True).offset(offset=skip).limit(limit=limit).all()
#                 return sites
#         except SQLAlchemyError as err:
#             logging.error(f"Error fetching all the sites.")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


#     def get_sites_by_id(self, site_id:int, tenancy_id:Optional[int]=None) -> Optional[Site]:
#         """
#         Retrieves a Sites by its ID.
#         """
#         try:
#             #site existence
#             if tenancy_id:
#                 site = self.get_by_id(id=site_id, tenancy_id=tenancy_id, is_active=True)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
#                 return site
#             else:
#                 site = self.get_by_id(id=site_id, is_active=True)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
#                 return site
#         except SQLAlchemyError as err:
#             logging.error(f"Error fetching the specific site.")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


#     def get_site_by_name(self, site_name:str, tenancy_id:Optional[int]=None) -> List[Site]:
#         """
#         Retrieves a Sites by its ID.
#         """
#         try:
#             #site existence
#             if tenancy_id:
#                 site = self.db_session.query(Site).filter(Site.is_active==True, Site.tenancy_id==tenancy_id, Site.name.ilike(f"%{site_name}%")).all()
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site name {site_name} supplied does not exist or not in your state")
#                 return site
#             else:
#                 site = self.db_session.query(Site).filter(Site.is_active==True, Site.name.ilike(f"%{site_name}%")).all()
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site name {site_name} supplied does not exist")
#                 return site
#         except SQLAlchemyError as err:
#             logging.error(f"Error fetching the specific site.")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


#     def update_site(self, site_id:int, site_data:SiteUpdate, tenancy_id:Optional[int]=None) -> Optional[Site]:
#         """
#         Updates an existing Site.
#         """
#         try:
#             if tenancy_id:
#                 #site existence
#                 site = self.get_sites_by_id(site_id=site_id, tenancy_id=tenancy_id)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
#             else:
#                 site = self.get_sites_by_id(site_id=site_id)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
            
#             update_site = self.update(db_obj=site, obj_in=site_data)
#             return update_site
#         except SQLAlchemyError as err:
#             logging.error(f"Error fetching the specific site.")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")
        

#     def delete_hard_site(self, site_id:int, tenancy_id:Optional[int]=None):
#         """
#         To hard delete a site permanently
#         """
#         try:
#             if tenancy_id:
#                 #Check for site existence
#                 site = self.get_sites_by_id(site_id=site_id, tenancy_id=tenancy_id)
#                 if not site:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
#             else:
#                 site = self.get_sites_by_id(site_id=site_id)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
            
#             self.db_session.delete(site)
#             self.db_session.commit()

#             return site_id
        
#         except SQLAlchemyError as err:
#             logging.error(f"Issue with {err}  ")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"There were issues while deleting site {str(err)} ")

            
    
#     def soft_delete_sites(self, site_id:int, tenancy_id:Optional[int]=None):
#         """
#         To soft-delete a site from a tenancy
#         """
#         try:
#             if tenancy_id:
#                 #check for site existence
#                 site = self.get_by_id(id=site_id, tenancy_id=tenancy_id)
#                 if not site:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
#             else:
#                 site = self.get_by_id(id=site_id)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
                
#             if not site.is_active:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Site with ID {site_id} is already deactivated !!!")
                
#             self.soft_delete(id=site_id)
#             return {f"message : The Site with site ID {site_id} has been deactivated successfully!!!"}
        
#         except SQLAlchemyError as err:
#             logging.error(f"Issue with {err}  ")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"There were issues while soft-deleting site {str(err)} ")
       
#     def restore_site(self, site_id:int, tenancy_id:Optional[int]=None) -> Optional[Site]:
#         """
#         To restore a site from a tenancy
#         """
#         try:
#             if tenancy_id:
#                 #check for site existence
#                 site = self.get_by_id(id=site_id, tenancy_id=tenancy_id)
#                 if not site:
#                         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
#             else:
#                 site = self.get_by_id(id=site_id)
#                 if not site:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
                
#             if site.is_active:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Site with ID {site_id} is already active !!!")
                
#             site.is_active = True
#             self.db_session.commit()
#             return site
        
#         except SQLAlchemyError as err:
#             logging.error(f"Issue with {err}  ")
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"There were issues while restoring site {str(err)} ")



from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from schemas.site_schemas import SiteCreate, SiteUpdate
from models.all_models import Site, Location
from repositories.base_repository import BaseRepository
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import logging



class SiteRepository(BaseRepository[Site, SiteCreate, SiteUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(Site, db_session)


    def create_site(self, site_data: SiteCreate) -> Site:
        """
        Creates a new Site ensuring that the site is unique within the Site table and Tenenant.
        """
        site_existence = (
            self.db_session.query(Site)
            .filter(Site.name == site_data.name, Site.tenancy_id == site_data.tenancy_id)
            .first()
        )
        if site_existence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Site with the name {site_data.name} already exists in this State with tenacncy_id {site_data.tenancy_id} !!!",
            )
        #check for location existence in the tenant
        location_existence = self.db_session.query(Location).filter(Location.id == site_data.location_id, Location.tenancy_id==site_data.tenancy_id).first()
        if not location_existence:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Kindly ensure the location ID {site_data.location_id} supplied to the new site is for the state")

        try:
            return self.create(site_data)
        except Exception as err:
            self.handle_errors(
                e=err, message=f"Database Error during Site creation {err}"
            )


    def get_all_sites(self, skip:int=0, limit:int=100, tenancy_id:Optional[int]=None) -> List[Site]:
        """
        Retrieves all Sites that are active with optional pagination.
        """
        try:
            if tenancy_id:
                sites = self.db_session.query(Site).filter(Site.is_active==True, Site.tenancy_id==tenancy_id).offset(offset=skip).limit(limit=limit).all()
                return sites
            else:
                sites = self.db_session.query(Site).filter(Site.is_active==True).offset(offset=skip).limit(limit=limit).all()
                return sites
        except SQLAlchemyError as err:
            logging.error(f"Error fetching all the sites.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


    def get_sites_by_id(self, site_id:int, tenancy_id:Optional[int]=None) -> Optional[Site]:
        """
        Retrieves a Sites by its ID.
        """
        try:
            #site existence
            if tenancy_id:
                site = self.db_session.query(Site).filter(Site.id==site_id, Site.is_active==True, Site.tenancy_id==tenancy_id).first()
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
                return site
            else:
                site = self.db_session.query(Site).filter(Site.id==site_id, Site.is_active==True).first()
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
                return site
        except SQLAlchemyError as err:
            logging.error(f"Error fetching the specific site.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


    def get_site_by_name(self, site_name:str, tenancy_id:Optional[int]=None) -> List[Site]:
        """
        Retrieves a Sites by its ID.
        """
        try:
            #site existence
            if tenancy_id:
                site = self.db_session.query(Site).filter(Site.is_active==True, Site.tenancy_id==tenancy_id, Site.name.ilike(f"%{site_name}%")).all()
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site name {site_name} supplied does not exist or not in your state")
                return site
            else:
                site = self.db_session.query(Site).filter(Site.is_active==True, Site.name.ilike(f"%{site_name}%")).all()
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site name {site_name} supplied does not exist")
                return site
        except SQLAlchemyError as err:
            logging.error(f"Error fetching the specific site.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


    def update_site(self, site_id:int, site_data:SiteUpdate, tenancy_id:Optional[int]=None) -> Optional[Site]:
        """
        Updates an existing Site.
        """
        try:
            if tenancy_id:
                #site existence
                site = self.get_sites_by_id(site_id=site_id, tenancy_id=tenancy_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
            else:
                site = self.get_sites_by_id(site_id=site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
            
            update_site = site_data.model_dump(exclude_unset=True)
            for key, value in update_site.items():
                setattr(site, key, value)
            
            self.db_session.commit()
            self.db_session.refresh(site)
            return {"message : Site updated successfully"}
        except SQLAlchemyError as err:
            logging.error(f"Error fetching the specific site.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")
        

    def delete_hard_site(self, site_id:int, tenancy_id:Optional[int]=None):
        """
        To hard delete a site permanently
        """
        try:
            if tenancy_id:
                #Check for site existence
                site = self.get_sites_by_id(site_id=site_id, tenancy_id=tenancy_id)
                if not site:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
            else:
                site = self.get_sites_by_id(site_id=site_id)
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
            
            self.db_session.delete(site)
            self.db_session.commit()

            return site_id
        
        except SQLAlchemyError as err:
            logging.error(f"Issue with {err}  ")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"There were issues while deleting site {str(err)} ")

            
    
    def soft_delete_sites(self, site_id:int, tenancy_id:Optional[int]=None):
        """
        To soft-delete a site from a tenancy
        """
        try:
            if tenancy_id:
                #check for site existence
                site = self.db_session.query(Site).filter(Site.id==site_id, Site.tenancy_id==tenancy_id).first()
                if not site:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
            else:
                site = self.db_session.query(Site).filter(Site.id==site_id).first()
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
                
            if not site.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Site with ID {site_id} is already deactivated !!!")
                
            site.is_active=False
            self.db_session.commit()
            self.db_session.refresh(site)

            return {f"message : The Site with site ID {site_id} has been deactivated successfully!!!"}
        
        
        except SQLAlchemyError as err:
            logging.error(f"Issue with {err}  ")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"There were issues while soft-deleting site {str(err)} ")
       
    def restore_site(self, site_id:int, tenancy_id:Optional[int]=None) -> Optional[Site]:
        """
        To restore a site from a tenancy
        """
        try:
            if tenancy_id:
                #check for site existence
                site = self.db_session.query(Site).filter(Site.id==site_id, Site.tenancy_id==tenancy_id).first()
                if not site:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist or not in your state")
            else:
                site = self.db_session.query(Site).filter(Site.id==site_id).first()
                if not site:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The site ID {site_id} supplied does not exist")
                
            if site.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Site with ID {site_id} is already active !!!")
                
            site.is_active = True
            self.db_session.commit()
            return {f"message : The Site with site ID {site_id} has been activated successfully!!!"}
        
        except SQLAlchemyError as err:
            logging.error(f"Issue with {err}  ")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"There were issues while restoring site {str(err)} ")