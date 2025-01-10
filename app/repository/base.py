import logging
from functools import wraps

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, IntegrityError
from fastapi import status, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from typing import final, List, Optional
from ..repository.utils import check_duplicate_parameter
from sqlalchemy.inspection import inspect

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)


def exception_catch_for_one(func):
    """
    This is an exception processing decorator function for instance function that does sql returning one
    """
    @wraps(func)
    def inner_function(*args, **kwargs):
        msg = f"Querying for one item from {args[0].table.__table__.schema}.{args[0].table.__table__.name}. "
        logger.info(msg)
        try:
            return func(*args, **kwargs)
        except NoResultFound as err:
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg + err.__str__())
        except MultipleResultsFound as err:
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg + err.__str__())
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")
    return inner_function


def create_exception_catch(func):
    """
    This is an exception processing decorator function
    """
    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as err:
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args)
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")
    return inner_function


class Singleton(type):
    _instances = {}

    # takes over __call__ function
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseRepo(object):
    def __init__(self, table):
        self.table = table

    def model_to_dict(self, model):
        '''
        turn an orm model into a dictionary
        '''
        return {c.key: getattr(model, c.key)
                for c in inspect(model).mapper.column_attrs}

    def count(self, db: Session):
        """
        return: item count of the table
        """
        return db.query(self.table).count()

    def list_all(self, db: Session, limit: Optional[int] = None, offset: Optional[int] = None):
        try:
            if limit is not None and offset is not None:
                return db.query(self.table).order_by(self.table.id.desc()).limit(limit).offset(offset).all()
            return db.query(self.table).all()
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")

    @final
    def get_single(self, id, db: Session):
        """
        This is a simple function to either return the item with the specified id
        queried from the table of BaseRepo, or raise NoResultFound err

        :param id: id to query in the table
        :param db: inherit database session from outer function
        :return: table item with id queried from the table
        """
        try:
            item = db.query(self.table).filter(self.table.id == id).one()
            return item
        except NoResultFound as err:
            msg = f"No result found for id {id} in table " \
                  f"{self.table.__table__.schema}.{self.table.__table__.name}"
            logger.error(msg, exc_info=True)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")

    def get_many(self, filters: dict,  db: Session, limit: Optional[int] = None, offset: Optional[int] = None):
        """
        This is a simple function to return all items queried from the table of BaseRepo

        :param filters: dict to pass in all filters, e.g. {"name": "John", "age": 30}
        :param db: inherit database session from outer function
        :return: table items queried from the table
        """
        try:
            if limit is not None and offset is not None:
                return db.query(self.table).filter_by(**filters).order_by(
                    self.table.id.desc()).limit(limit).offset(offset).all()
            return db.query(self.table).filter_by(**filters).all()
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")

    def create_single(self, request, db: Session):
        """
        This is a simple function to create one item inserted into self table

        :param request: request body to specify new item input schema
        :param db: inherit database session from outer function
        :return: new item inserted into the self table
        """
        try:
            item_data = jsonable_encoder(request)
            parameters = item_data.get('parameters')
            if parameters is not None:
                check_duplicate_parameter(parameters)
            new_item = self.table(**item_data)
        except ValueError as err:
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.args)
        item = self._insert_row(new_item=new_item, db=db)
        return item

    @create_exception_catch
    def _insert_row(self, new_item, db):
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    def create_many(self, request, db: Session):
        """
        This is a simple function to create a list of items inserted into self table

        :param request: a list of new item input schemas
        :param db: inherit database session from outer function
        :return: a list of new items inserted into the self table
        """
        new_items = []
        try:
            for input_body in request:
                item_data = jsonable_encoder(input_body)
                parameters = item_data.get('parameters')
                if parameters is not None:
                    check_duplicate_parameter(parameters)
                item = self.table(**item_data)
                new_items.append(item)
            db.add_all(new_items)
            db.commit()
            for new_item in new_items:
                db.refresh(new_item)
            return new_items
        except IntegrityError as err:
            db.rollback()
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args)
        except Exception as err:
            db.rollback()
            for item in new_items:
                db.delete(item)
            db.commit()
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")

    def get_single_by_column(self, filters: dict, db: Session):
        """
        This is a simple function to either return the item with the specified filters
        queried from self.table, or raise NoResultFound err

        :param filters: filters holding the key:column,value:value to query in the table
        :param db: inherit database session from outer function
        :return: table item with id queried from the table
        """
        try:
            item = db.query(self.table).filter_by(**filters).one()
            return item
        except NoResultFound as err:
            msg = f"No result found for filters {filters} in table " \
                  f"{self.table.__table__.schema}.{self.table.__table__.name}"
            logger.error(msg, exc_info=True)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        except MultipleResultsFound as err:
            msg = f"Multiple results found for filters {filters} in table " \
                  f"{self.table.__table__.schema}.{self.table.__table__.name}"
            logger.error(msg, exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")

    def delete_single(self, id, db: Session):
        """
        This is a simple function to delete the item with the specified id
        queried from the table of BaseRepo, or raise NoResultFound err

        :param id: id to query in the table
        :param db: inherit database session from outer function
        :return: empty response object
        """
        item_to_delete = self.get_single(id, db)  # test if the item exists
        try:
            db.delete(item_to_delete)
            db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except IntegrityError as err:
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args)
        except Exception as err:
            logger.error(f"{err.__class__}: {err.__str__()}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{err.__class__}: {err.__str__()}")

    @create_exception_catch
    def delete_many(self, items: list, db: Session):
        """
        This is  function to delete items pass in
        queried from the table of BaseRepo, or raise NoResultFound err

        :param items: items to be deleted
        :param db: inherit database session from outer function
        :return: empty response object
        """
        if len(items) == 0:
            return 'Empty item list to delete; no action taken'
        for item in items:
            db.delete(item)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def update_single(self, id, request: dict, db: Session):
        """
        This is a simple function to update an item in the table of BaseRepo,
        or raise NoResultFound err

        :param id: id to query in the table
        :param request: request body (of update schema) of the item, {field: value, ...}
        :param db: inherit database session from outer function
        :return: new item created in the table
        """
        row_to_be_updated = self.get_single(id, db)
        return self._update_row(item=row_to_be_updated, request=request, db=db)

    def _update_row(self, item, request, db: Session):
        """
        This is a inner function to update an row in the table of BaseRepo,
        or raise NoResultFound err

        :row_to_be_updated: the row object that you want to update
        :param request: request body (of update schema) of the item
        :param db: inherit database session from outer function
        :return: new item created in the table
        """
        try:
            item_data = jsonable_encoder(item)
            if isinstance(request, dict):
                update_data = request
            else:
                update_data = request.dict(exclude_unset=True)
            for field in item_data:
                if field in update_data:
                    if field == 'parameters':
                        check_duplicate_parameter(update_data[field])
                    setattr(item, field, update_data[field])
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        except IntegrityError as err:
            db.rollback()
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args)
        except ValueError as err:
            logger.error(err, exc_info=True)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.args)

    def _upsert_row(self, unique_filter, request, db: Session):
        """
        This is a inner function to upsert (insert or update) a row in the table of BaseRepo,
        or raise NoResultFound err

        :param item_id: the primary key of the item
        :param request: request body (of update schema) of the item
        :param db: inherit database session from outer function
        :return: new item created or updated in the table
        """
        try:
            item = db.query(self.table).filter_by(**unique_filter).one()
            return self.update_single(item.id, request, db)
        except NoResultFound:
            return self.create_single(request, db=db)

    # def _upsert_many_rows(self, items_request, db: Session):
    #     """
    #     This is a inner function to upsert (insert or update) multiple rows in the table of BaseRepo.

    #     :param items_request: a list of tuples, each containing the primary key and request body (of update schema) of an item
    #     :param db: inherit database session from outer function
    #     :return: list of new items created or updated in the table
    #     """
    #     upserted_items = []

    #     for item_id, request in items_request:
    #         upserted_item = self._upsert_row(item_id, request, db)
    #         upserted_items.append(upserted_item)

    #     return upserted_items
    
    def upsert_single(self, unique_filter, request, db: Session):
        """
        This is a simple function to upsert (insert or update) an item in the table of BaseRepo,
        or raise NoResultFound err

        :param id: id to query in the table
        :param request: request body (of update schema) of the item
        :param db: inherit database session from outer function
        :return: new item created or updated in the table
        """
        return self._upsert_row(unique_filter=unique_filter, request=request, db=db)
    