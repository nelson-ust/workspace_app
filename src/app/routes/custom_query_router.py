from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.custom_query_schema import QueryParameters
from repositories.custom_query_repository import CustomQueryRepository
from db.database import get_db
from logging_helpers import logging_helper

router = APIRouter()

@router.post("/custom-query")
async def custom_query(params: QueryParameters, db: Session = Depends(get_db)):
    logging_helper.log_info(params.dict())
    repository = CustomQueryRepository(db)
    try:
        result = repository.execute_custom_query(
            model_name=params.model,
            columns=params.columns,
            filters=params.filters,
            order_by=params.order_by,
            limit=params.limit,
            offset=params.offset,
            join_tables=params.join_tables
        )
        logging_helper.log_info(result)
        return result
    except ValueError as e:
        logging_helper.log_error(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging_helper.log_error(e)
        raise HTTPException(status_code=500, detail=f"An error occurred while performing the custom query: {str(e)}")
