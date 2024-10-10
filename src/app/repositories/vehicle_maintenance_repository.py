from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from schemas.vehicle_maintenance_schemas import VehicleMaintenanceCreate, VehicleMaintenanceUpdate
from models.all_models import MaintenanceType, VehicleMaintenance, Vehicle, Tenancy
from repositories.base_repository import BaseRepository
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Optional, List, Type
from logging_helpers import logging_helper


class VehicleMaintenanceRepository(BaseRepository[VehicleMaintenance, VehicleMaintenanceCreate, VehicleMaintenanceUpdate]):
    def __init__(self, db_session: Session):
        super().__init__(VehicleMaintenance, db_session)



    def create_vehiclemaintenance(self, vehiclemaintenance_data:VehicleMaintenanceCreate) -> VehicleMaintenance:
        try:
            #vehicle_maintenance existence
            vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.maintenance_date==vehiclemaintenance_data.maintenance_date, VehicleMaintenance.vehicle_id==VehicleMaintenance.vehicle_id).first()
            if vehicle_maintenance:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The VehicleMaintenance has already been created")
            
            #tenancy check
            tenancy_existence = self.db_session.query(Tenancy).filter(Tenancy.id == vehiclemaintenance_data.tenancy_id, Tenancy.is_active==True).first()
            if not tenancy_existence:
                logging_helper.log_info(f"The Tenancy ID: {vehiclemaintenance_data.tenancy_id} supplied does not exist")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The Tenancy ID supplied does not exist")
            
            new_vehicle_maintenance = self.create(obj_in=vehiclemaintenance_data)
            return new_vehicle_maintenance
        
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Creation of VehicleMaintenance failed {err}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating VehicleMaintenance {str(err)}")
        


    def get_all_vehicle_maintenance(self, skip:int =0, limit:int =100, tenancy_id:Optional[int] = None) -> List[VehicleMaintenance]:
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all VehicleMaintenance for the state
            if tenancy_id:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.is_active==True, VehicleMaintenance.tenancy_id==tenancy_id).offset(offset=skip).limit(limit=limit).all()
                return vehicle_maintenance
            
            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            else:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.is_active==True).offset(offset=skip).limit(limit=limit).all()
                return vehicle_maintenance
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error fetching the VehicleMaintenances.: {str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")
        

    def get_vehicle_maintenance_by_id(self, vehicle_maintenance_id:int, tenancy_id:Optional[int]=None) -> VehicleMaintenance:
        """
        Retrieves a VehicleMaintenance by its ID.
        """
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all VehicleMaintenance for the state
            if tenancy_id:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.is_active==True, VehicleMaintenance.tenancy_id==tenancy_id, VehicleMaintenance.id==vehicle_maintenance_id).first()
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist or not in your state")
                return vehicle_maintenance
        
            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            else:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.is_active==True, VehicleMaintenance.id==vehicle_maintenance_id).first()
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist")
                return vehicle_maintenance
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error fetching the specific VehicleMaintenance: {str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")
        

    def update_vehicle_maintenance(self, vehicle_maintenance_id:int, vehicle_maintenance_data:VehicleMaintenanceUpdate, tenancy_id:Optional[int]=None) -> VehicleMaintenance:
        """
        Updates an existing VehicleMaintenance.
        """
        try:
             ##For Admin, Chief Driver and Tenant Admin to map all VehicleMaintenance for the state
            if tenancy_id:
                vehicle_maintenance = self.get_vehicle_maintenance_by_id(vehicle_maintenance_id=vehicle_maintenance_id, tenancy_id=tenancy_id)
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist or not in your state")
            
            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            else:
                vehicle_maintenance = self.get_vehicle_maintenance_by_id(vehicle_maintenance_id=vehicle_maintenance_id)
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist")
            
            update_vehicle_maintenance = self.update(db_obj=vehicle_maintenance, obj_in=vehicle_maintenance_data)
            return update_vehicle_maintenance
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error fetching the specific VehicleMaintenance. {str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error due to {str(err)}")


    def delete_hard_vehicle_maintenance(self, vehicle_maintenance_id:int, tenancy_id:Optional[int]=None):
            try:
                ##For Admin, Chief Driver and Tenant Admin to map all VehicleMaintenance for the state
                if tenancy_id:
                    vehicle_maintenance = self.get_vehicle_maintenance_by_id(vehicle_maintenance_id=vehicle_maintenance_id, tenancy_id=tenancy_id)
                    if not vehicle_maintenance:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist or not in your state")
                
                ##For Super Admin mapping all the VehicleMaintenance for the 3 States
                else:
                    vehicle_maintenance = self.get_vehicle_maintenance_by_id(vehicle_maintenance_id=vehicle_maintenance_id)
                    if not vehicle_maintenance:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist")
                
                self.db_session.delete(vehicle_maintenance)
                self.db_session.commit()
                return vehicle_maintenance_id
            except SQLAlchemyError as err:
                logging_helper.log_error(f"Error hard deleting the specific VehicleMaintenance.")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error deleting VehicleMaintenance due to {str(err)}")
            

    def soft_delete_vehicle_maintenance(self, vehicle_maintenance_id:int, tenancy_id:Optional[int]=None):
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all VehicleMaintenance for the state
            if tenancy_id:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.tenancy_id==tenancy_id, VehicleMaintenance.id==vehicle_maintenance_id).first()
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist or not in your state")
            
            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            else:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.id==vehicle_maintenance_id).first()
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist")
                
            if not vehicle_maintenance.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The VehicleMaintenance with ID {vehicle_maintenance_id} is already deactivated !!!")
            
            self.soft_delete(id=vehicle_maintenance_id)
            return {f"message : The VehicleMaintenance with VehicleMaintenance ID {vehicle_maintenance_id} has been deactivated successfully!!!"}
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error hard deleting the specific VehicleMaintenance.{str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error deleting VehicleMaintenance due to {str(err)}")
        
    
    def restore_vehicle_maintenance(self, vehicle_maintenance_id:int, tenancy_id:Optional[int]=None) -> VehicleMaintenance:
        try:
            ##For Admin, Chief Driver and Tenant Admin to map all VehicleMaintenance for the state
            if tenancy_id:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.tenancy_id==tenancy_id, VehicleMaintenance.id==vehicle_maintenance_id).first()
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist or not in your state")
            
            ##For Super Admin mapping all the VehicleMaintenance for the 3 States
            else:
                vehicle_maintenance = self.db_session.query(VehicleMaintenance).filter(VehicleMaintenance.id==vehicle_maintenance_id).first()
                if not vehicle_maintenance:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The VehicleMaintenance ID {vehicle_maintenance_id} supplied does not exist")
                
            if vehicle_maintenance.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The VehicleMaintenance with ID {vehicle_maintenance_id} is already active !!!")
            
            vehicle_maintenance.is_active = True
            self.db_session.commit()
            return vehicle_maintenance
        except SQLAlchemyError as err:
            logging_helper.log_error(f"Error hard deleting the VehicleMaintenance with id: {vehicle_maintenance_id}: {str(err)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There is error deleting VehicleMaintenance due to {str(err)}")
        

    def get_vehicle_maintenance_logs(self, start_date: datetime, end_date: datetime, tenancy_id: Optional[int] = None) -> List[Dict]:
        """
        Retrieves detailed vehicle maintenance logs, including vehicle and tenancy details, filtered by date range and optional tenancy.
        """
        try:
            query = self.db_session.query(VehicleMaintenance).join(Vehicle).join(Tenancy).join(MaintenanceType).options(
                joinedload(VehicleMaintenance.vehicle),
                joinedload(VehicleMaintenance.tenancy),
                joinedload(VehicleMaintenance.maintenance_type)
            ).filter(VehicleMaintenance.maintenance_date.between(start_date, end_date))

            if tenancy_id:
                query = query.filter(VehicleMaintenance.tenancy_id == tenancy_id)

            maintenance_logs = query.all()

            detailed_logs = []
            for log in maintenance_logs:
                detailed_log = {
                    "maintenance_id": log.id,
                    "maintenance_date": log.maintenance_date,
                    "description": log.description,
                    "cost": log.cost,
                    "vehicle": {
                        "id": log.vehicle.id,
                        "name": log.vehicle.name,
                        "licence_plate": log.vehicle.licence_plate,
                        "make": log.vehicle.make,
                        "year": log.vehicle.year,
                        "fuel_type": log.vehicle.fuel_type,
                        "seat_capacity": log.vehicle.seat_capacity,
                    },
                    "tenancy": {
                        "id": log.tenancy.id,
                        "name": log.tenancy.name,
                    },
                    "maintenance_type": {
                        "id": log.maintenance_type.id,
                        "name": log.maintenance_type.name,
                    }
                }
                detailed_logs.append(detailed_log)

            return detailed_logs

        except SQLAlchemyError as e:
            logging_helper.log_error(f"Error retrieving vehicle maintenance logs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve vehicle maintenance logs: {str(e)}",
            )