from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc, inspect
from typing import List, Dict, Any, Type

class QueryBuilder:
    def __init__(self, db_session: Session, model: Type):
        self.db_session = db_session
        self.model = model
        self.query = self.db_session.query(self.model)
        self.models = {model.__name__: model}
        self.related_models = []

    def join(self, related_models: List[str]):
        for related_model_name in related_models:
            related_model = self.get_model_by_name(related_model_name)
            if not self.is_relationship_valid(related_model):
                raise ValueError(f"No valid relationship found for joining: {related_model_name}")
            self.query = self.query.join(related_model)
            self.models[related_model.__name__] = related_model
            self.related_models.append(related_model)
        return self

    def is_relationship_valid(self, related_model: Type):
        mapper = inspect(self.model)
        for relationship in mapper.relationships:
            if relationship.mapper.class_ == related_model:
                return True
        return False

    def filter(self, filters: List[Dict[str, Any]]):
        conditions = []
        for condition in filters:
            table, column, operator, value = condition['table'], condition['column'], condition['operator'], condition['value']
            model = self.get_model_by_name(table)
            column = getattr(model, column)
            if operator == 'eq':
                conditions.append(column == value)
            elif operator == 'ne':
                conditions.append(column != value)
            elif operator == 'lt':
                conditions.append(column < value)
            elif operator == 'le':
                conditions.append(column <= value)
            elif operator == 'gt':
                conditions.append(column > value)
            elif operator == 'ge':
                conditions.append(column >= value)
            elif operator == 'in':
                conditions.append(column.in_(value))
            elif operator == 'like':
                conditions.append(column.like(f"%{value}%"))
            elif operator == 'ilike':
                conditions.append(column.ilike(f"%{value}%"))
            elif operator == 'between':
                conditions.append(column.between(value[0], value[1]))
        self.query = self.query.filter(and_(*conditions))
        return self

    def order_by(self, order_by: List[str]):
        if order_by:
            order_criteria = []
            for field in order_by:
                if field.startswith('-'):
                    model_name, column_name = field[1:].split('.')
                    order_criteria.append(desc(getattr(self.get_model_by_name(model_name), column_name)))
                else:
                    model_name, column_name = field.split('.')
                    order_criteria.append(asc(getattr(self.get_model_by_name(model_name), column_name)))
            self.query = self.query.order_by(*order_criteria)
        return self

    def limit(self, limit: int):
        if limit:
            self.query = self.query.limit(limit)
        return self

    def offset(self, offset: int):
        if offset:
            self.query = self.query.offset(offset)
        return self

    def columns(self, columns: Dict[str, List[str]]):
        selected_columns = []
        for table, cols in columns.items():
            model = self.get_model_by_name(table)
            for col in cols:
                selected_columns.append(getattr(model, col))
        self.query = self.query.with_entities(*selected_columns)
        return self

    def get_model_by_name(self, name: str):
        if name in self.models:
            return self.models[name]
        raise ValueError(f"Unsupported table for columns: {name}")

    def build(self):
        return self.query.all()
