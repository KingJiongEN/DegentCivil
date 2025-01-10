import logging


from io import BytesIO
from functools import lru_cache
import traceback
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import List
from app.database.base_database import get_db_context

# from fastapi import Response, HTTPException, status
# from fastapi.encoders import jsonable_encoder

from app.repository.base import BaseRepo
from app.database.orm import AgentRecord


class AgentRepo(BaseRepo):
    def __init__(self, table):
        super().__init__(table)
        
    def check_balance_and_raise(self, _id:int, balance_change:int, db: Session):
        try:
            # 查询指定ID的记录
            record = db.query(self.table).filter(self.table.id == _id).one_or_none()
            if record:
                #判断price值
                if record.gold + balance_change < 0:
                    raise ValueError(f'Sorry, there is only {record.gold} gold coins in the account.')
                    
                # 修改price值
                record.gold += balance_change
                db.commit()  # 显式提交更改
                print(f"Agent ID {_id} balance updated.")
                return record.gold
            else:
                raise NoResultFound(f"No agent found with ID {_id}.")
        except Exception as e:
            db.rollback()  # 发生异常时回滚更改
            raise AssertionError(f"Error updating agent ID {_id}: {e}")
        finally:
            db.close()  # 确保会话被关闭 
            
agent_record_repo = AgentRepo(table=AgentRecord)

def check_balance_and_raise(agent_id: int, balance_change: int):
    """
    Check if the artwork belongs to the owner.
    """
    with get_db_context() as db:
        try:
            agent_id = str(agent_id)
            return agent_record_repo.check_balance_and_raise(agent_id, balance_change=balance_change, db=db)
        except Exception as e:
            traceback.print_exc()
            raise e

def add_agent_to_db(info_dict):
    # Retrieve all column names from the ArtworkRecord class
    valid_keys = {column.name for column in AgentRecord.__table__.columns}
    # Filter the incoming dictionary to only include keys that are valid column names
    filtered_dict = {key: value for key, value in info_dict.items() if key in valid_keys} 
    record = AgentRecord(**filtered_dict) #FIXME
    

    with get_db_context() as db:
        new_event = agent_record_repo.table(
            **filtered_dict
            )
        
        db.add(new_event)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)

def update_agent_in_db(agent_id: int, update_dict: dict):
    """
    Updates a trade record in the database.
    
    :param record_id: The ID of the trade record to update
    :param trade_date: The new trade date (optional)
    :param amount: The new amount (optional)
    """
    with get_db_context() as db:
        agent_id = str(agent_id)
        agent_record_repo.update_single(agent_id, update_dict,db)
        
            
def get_agent_from_db(agent_id: int):
    """
    Retrieves a trade record from the database.
    
    :param record_id: The ID of the trade record to retrieve
    """
    with get_db_context() as db:
        try:
            agent_id = str(agent_id)
            agent = agent_record_repo.get_single(agent_id, db)
            return agent_record_repo.model_to_dict(agent)
        except Exception as e:
            logging.error(f"Error retrieving trade record from database: {e}")
            raise e

if __name__ == "__main__":
    print('use')
    # from app.database.base_database import get_db_context,init_db
    # init_db()
    # print('Database initialized.')
    # with get_db_context() as db:
    #     new_event = agent_record_repo.table(
    #         artwork_type="test_type",
    #         resource_id="test_resource_id",
    #         resource="test_resource",
    #         owner_id = "test_owner_id",
    #         owner_name="test_owner_name",
    #         prompt = "test_prompt",
    #         create_place_id = "test_place_id",
    #         create_place_name = 'test_create_place_name',
    #         timestamp=1000000000,
    #         price = 10
    #         )
            
    #     db.add(new_event)
    #     try:
    #         db.commit()
    #     except Exception as e:
    #         db.rollback()
    #         print(e)