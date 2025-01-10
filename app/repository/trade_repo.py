import logging


from io import BytesIO
from functools import lru_cache
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import List
from app.database.base_database import get_db_context

# from fastapi import Response, HTTPException, status
# from fastapi.encoders import jsonable_encoder

from app.repository.base import BaseRepo
from app.database.orm import TradeRecord


class TradeRepo(BaseRepo):
    def __init__(self, table):
        super().__init__(table)
        

trade_record_repo = TradeRepo(table=TradeRecord)

def add_trade_to_db(info_dict):
    # Retrieve all column names from the ArtworkRecord class
    valid_keys = {column.name for column in TradeRecord.__table__.columns}
    # Filter the incoming dictionary to only include keys that are valid column names
    filtered_dict = {key: value for key, value in info_dict.items() if key in valid_keys} 
    

    with get_db_context() as db:
        new_event = trade_record_repo.table(
            **filtered_dict
            )
        
        db.add(new_event)
        try:
            db.commit()
            print(f"Trade record added to database: {new_event.id}")
        except Exception as e:
            db.rollback()
            print(e)


            
def get_traderecord_from_db(record_id: int):
    """
    Retrieves a trade record from the database.
    
    :param record_id: The ID of the trade record to retrieve
    """
    with get_db_context() as db:
        try:
            record = trade_record_repo.get_single(record_id, db)
            return trade_record_repo.model_to_dict(record)
        except Exception as e:
            logging.error(f"Error retrieving trade record from database: {e}")
            raise e

if __name__ == "__main__":
    from app.database.base_database import get_db_context,init_db
    init_db()
    print('Database initialized.')
    with get_db_context() as db:
        new_event = trade_record_repo.table(
            artwork_type="test_type",
            resource_id="test_resource_id",
            resource="test_resource",
            owner_id = "test_owner_id",
            owner_name="test_owner_name",
            prompt = "test_prompt",
            create_place_id = "test_place_id",
            create_place_name = 'test_create_place_name',
            timestamp=1000000000,
            price = 10
            )
            
        db.add(new_event)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)