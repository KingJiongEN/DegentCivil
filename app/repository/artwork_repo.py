import logging


from io import BytesIO
from functools import lru_cache
import traceback
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import List
from ..repository.base import BaseRepo
from ..database.orm import ArtworkRecord
from app.database.base_database import get_db_context


class ArtworkRepo(BaseRepo):
    def __init__(self, table):
        super().__init__(table)


artwork_record_repo = ArtworkRepo(table=ArtworkRecord)


def check_artwork_belonging(artwork_id: int, owner_id: int):
    """
    Check if the artwork belongs to the owner.
    """
    with get_db_context() as db:
        try:
            record = artwork_record_repo.get_single(artwork_id, db)
            if str(record.owner_id) == str(owner_id):
                return True
            else:
                return False
        except Exception as e:
            traceback.print_exc()
            raise e

def add_artwork_to_db(info_dict):
    # Retrieve all column names from the ArtworkRecord class
    valid_keys = {column.name for column in ArtworkRecord.__table__.columns}
    # Filter the incoming dictionary to only include keys that are valid column names
    filtered_dict = {key: value[:255] if type(value) is str else value for key, value in info_dict.items() if key in valid_keys} 
    record = ArtworkRecord(**filtered_dict) #FIXME
    
    # global_artworks[record.resource_id] = record    
    print(f"record.id: {record.id} added")

    with get_db_context() as db:
        new_event = artwork_record_repo.table(
            **filtered_dict
            )
        
        db.add(new_event)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)

def update_artwork_in_db(artwork_id: str, request: dict):
    """
    Updates an artwork record in the database.
    
    :param record_id: The ID of the trade record to update
    :param request: a dictionary of the fields to update
    
    """
    with get_db_context() as db:
        # record = db.query(artwork_record_repo.table).filter(artwork_record_repo.table.id == artwork_id).one_or_none()
        artwork_record_repo.upsert_single({"id": artwork_id}, request, db) 
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
            
def get_artwork_from_db(_id):
    """
    Retrieves a record from the database.
    
    :param _id: The ID of the  record to retrieve
    """
    with get_db_context() as db:
        # record = db.query(artwork_record_repo.table).filter(artwork_record_repo.table.id == artwork_id).one_or_none()
        art_work = artwork_record_repo.get_single(_id, db)
        art_work = artwork_record_repo.model_to_dict(art_work)
        try:
            db.commit()
            return art_work
        except Exception as e:
            db.rollback()
            raise ValueError(e)

if __name__ == "__main__":
    from app.database.base_database import get_db_context,init_db
    init_db()
    print('Database initialized.')
    with get_db_context() as db:
        new_event = artwork_record_repo.table(
            artwork_type="test_type",
            id="test_resource_id",
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
        
    with get_db_context() as db:

        artwork_record_repo.check_price_and_raise(
            _id=1,
            db=db
        )