
# from datetime import datetime
# import logging
# from psycopg2 import DataError, IntegrityError, OperationalError
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from fastapi import HTTPException
# from typing import Generic, Type, TypeVar, Optional, List
# from pydantic import BaseModel
# from models.all_models import BaseTable
# from logging_helpers import logging_helper

# ModelType = TypeVar("ModelType", bound=BaseTable)
# CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
#     def __init__(self, model: Type[ModelType], db_session: Session):
#         self.model = model
#         self.db_session = db_session

#     def get_by_id(self, id: int, tenancy_id:Optional[int]=None) -> Optional[ModelType]:
        
#         query=self.db_session.query(self.model).filter(self.model.id == id,self.model.is_active==True).first()
#         if tenancy_id:
#             query = query.filter(self.model.tenancy_id == tenancy_id)
#         try:
#             return query.first()
#         except Exception as e:
#             logging_helper.log_error(f"Failed to retrieve {self.model} by ID") 

# #     def get_by_id(
# #         self,
# #         id: int,
# #         tenancy_id: Optional[int] = None,
# #         is_active: Optional[bool] = False,
# #     ) -> Optional[T]:
# #         query = self.db_session.query(self.model).filter(self.model.id == id)
# #         if is_active:
# #             query = query.filter(self.model.is_active == is_active)
# #         if tenancy_id:
# #             query = query.filter(self.model.tenancy_id == tenancy_id)
# #         try:
# #             return query.first()
# #         except Exception as e:
# #             self.handle_errors(e, f"Failed to retrieve {self.model} by ID")


#     def get_all(self, skip: int = 0, limit: int = 100, tenancy_id: Optional[int]=None) -> List[ModelType]:
        
#         query=self.db_session.query(self.model).filter(self.model.is_active==True).offset(skip).limit(limit).all()

#         if tenancy_id:
#             query.query.filter(self.model.tenancy_id==tenancy_id)
#         try:
#             return query.offset(skip).limit(limit).all()
#         except Exception as e:
#             logging_helper.log_error(f"Failed to retrieve all {self.model}s")

#     def create(self, obj_in: CreateSchemaType) -> ModelType:
#         obj_in_data = obj_in.dict()
#         db_obj = self.model(**obj_in_data)
#         self.db_session.add(db_obj)
#         self.db_session.commit()
#         self.db_session.refresh(db_obj)
#         return db_obj

#     def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
#         obj_data = db_obj.dict()
#         update_data = obj_in.dict(skip_defaults=True)
#         for field in obj_data:
#             if field in update_data:
#                 setattr(db_obj, field, update_data[field])
#         self.db_session.commit()
#         self.db_session.refresh(db_obj)
#         return db_obj

#     def delete(self, id: int) -> Optional[ModelType]:
#         obj = self.get_by_id(id)
#         if obj:
#             self.db_session.delete(obj)
#             self.db_session.commit()
#         return obj

#     def delete_hard(self, id: int):
#         obj = self.get_by_id(id)
#         if obj:
#             self.db_session.delete(obj)
#             self.db_session.commit()

#     def soft_delete(self, id: int, user_id: int) -> Optional[ModelType]:
#         obj = self.get_by_id(id)
#         if obj:
#             obj.is_active = False
#             obj.date_deleted = datetime.utcnow()
#             self.db_session.commit()
#         return obj


#     def handle_errors(self, e, message: str):
#         logging.error(f"{message}: {str(e)}")
#         self.db_session.rollback()

#         if isinstance(e, IntegrityError):
#             raise HTTPException(
#                 status_code=400, detail=f"{message}: Integrity constraint violation."
#             )
#         elif isinstance(e, OperationalError):
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"{message}: Operational issue with the database.",
#             )
#         elif isinstance(e, DataError):
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"{message}: Data error (e.g., datatype mismatch).",
#             )
#         elif isinstance(e, SQLAlchemyError):
#             raise HTTPException(
#                 status_code=500, detail=f"{message} due to a database error"
#             )
#         else:
#             raise HTTPException(
#                 status_code=500, detail=f"{message}"
#             )




from datetime import datetime
import logging
from psycopg2 import DataError, IntegrityError, OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import Generic, Type, TypeVar, Optional, List
from pydantic import BaseModel
from models.all_models import BaseTable
from logging_helpers import logging_helper

ModelType = TypeVar("ModelType", bound=BaseTable)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db_session = db_session

    def get_by_id(self, id: int, tenancy_id:Optional[int]=None) -> Optional[ModelType]:
        
        query=self.db_session.query(self.model).filter(self.model.id == id,self.model.is_active==True)
        if tenancy_id:
            query = query.filter(self.model.tenancy_id == tenancy_id)
        try:
            return query.first()
        except Exception as e:
            logging_helper.log_error(f"Failed to retrieve {self.model} by ID") 

#     def get_by_id(
#         self,
#         id: int,
#         tenancy_id: Optional[int] = None,
#         is_active: Optional[bool] = False,
#     ) -> Optional[T]:
#         query = self.db_session.query(self.model).filter(self.model.id == id)
#         if is_active:
#             query = query.filter(self.model.is_active == is_active)
#         if tenancy_id:
#             query = query.filter(self.model.tenancy_id == tenancy_id)
#         try:
#             return query.first()
#         except Exception as e:
#             self.handle_errors(e, f"Failed to retrieve {self.model} by ID")


    def get_all(self, skip: int = 0, limit: int = 100, tenancy_id: Optional[int]=None) -> List[ModelType]:
        
        query=self.db_session.query(self.model).filter(self.model.is_active==True)

        if tenancy_id:
            query.query.filter(self.model.tenancy_id==tenancy_id)
        try:
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logging_helper.log_error(f"Failed to retrieve all {self.model}s")

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        self.db_session.add(db_obj)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = db_obj.dict()
        update_data = obj_in.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> Optional[ModelType]:
        obj = self.get_by_id(id)
        if obj:
            self.db_session.delete(obj)
            self.db_session.commit()
        return obj

    def delete_hard(self, id: int):
        obj = self.get_by_id(id)
        if obj:
            self.db_session.delete(obj)
            self.db_session.commit()

    def soft_delete(self, id: int, user_id: int) -> Optional[ModelType]:
        obj = self.get_by_id(id)
        if obj:
            obj.is_active = False
            obj.date_deleted = datetime.utcnow()
            self.db_session.commit()
        return obj


    def handle_errors(self, e, message: str):
        logging.error(f"{message}: {str(e)}")
        self.db_session.rollback()

        if isinstance(e, IntegrityError):
            raise HTTPException(
                status_code=400, detail=f"{message}: Integrity constraint violation."
            )
        elif isinstance(e, OperationalError):
            raise HTTPException(
                status_code=500,
                detail=f"{message}: Operational issue with the database.",
            )
        elif isinstance(e, DataError):
            raise HTTPException(
                status_code=400,
                detail=f"{message}: Data error (e.g., datatype mismatch).",
            )
        elif isinstance(e, SQLAlchemyError):
            raise HTTPException(
                status_code=500, detail=f"{message} due to a database error"
            )
        else:
            raise HTTPException(
                status_code=500, detail=f"{message}"
            )
