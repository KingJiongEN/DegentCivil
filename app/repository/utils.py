"""
Utils functions for kithara repository
"""

from datetime import datetime
import logging
import random
import uuid
import numpy as np
import io
import pandas as pd
from typing import List, Optional, Union, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Pagination:
    __slots__ = ['page', 'page_size']

    def __init__(self, page: int, page_size: int):
        self.page = page
        self.page_size = page_size

    @property
    def limit(self):
        return self.page_size

    @property
    def offset(self):
        return (self.page - 1) * self.page_size


def pagination_dependency(page: Optional[int] = None, page_size: Optional[int] = None) -> Pagination:
    """
    page and page_size are optional default to None
    """
    if page and page_size:
        return Pagination(page, page_size)
    return None


def paginate(obj: list, page: int, page_size: int):
    """
    Home made pagination function
    """
    return obj[(page - 1) * page_size: page * page_size] if page * page_size < len(obj) else obj[(page - 1) * page_size:]


def levenshtein_distance(string1: str, string2: str) -> float:
    """
    Calculate the Levenshtein distance between two strings.
    :param string1: string 1
    :param string2: string 2
    :return: the Levenshtein distance between two strings
    """
    array = np.zeros(shape=(len(string1)+1, len(string2)+1))
    for i in range(len(string2)+1):
        array[0][i] = i
    for i in range(len(string1)+1):
        array[i][0] = i
    for i in range(1, len(string1)+1):
        for j in range(1, len(string2)+1):
            if string1[i-1] == string2[j-1]:
                array[i][j] = min(array[i-1][j]+1, array[i][j-1]+1, array[i-1][j-1]+0)
            else:
                array[i][j] = min(array[i-1][j], array[i][j-1], array[i-1][j-1])+1
    ld = array[-1][-1]
    return 1 - (ld/(max(len(string1), len(string2))))


def general_delete(table_items, db):
    """
    The function rollbacks a list of items in a database table by iteratively delete each

    :param table_items: a list of table model items
    :param db: db session inherited from outer function
    """
    try:
        for item in table_items:
            db.delete(item)
            logger.info(f'(ROLLBACK) Deleting {item.__table__.schema} {item.__table__.name} with id {item.id}')
        db.commit()
    except:
        logger.error(f'Fail to delete {item.__table__.schema} {item.__table__.name} with id {item.id}')
        return None


def check_duplicate_parameter(parameters: List[dict]):
    """
    check if parameter values of the parameter field are unique,
    if not raise an error, should be called before instantiating a new DB object that has a parameter field
    and when updating a DB object that has a parameter field.
    :param parameters: list of parameters, each parameter is a dictionary
    """
    if parameters is None:
        return
    parameter_field = [parameter.get('parameter') for parameter in parameters]
    if duplicate_parameters := {x for x in parameter_field if parameter_field.count(x) > 1}:
        raise ValueError(f"Duplicate parameter name: {duplicate_parameters}")

from .agent_repo import check_balance_and_raise, update_agent_in_db
from .artwork_repo import update_artwork_in_db
from .trade_repo import add_trade_to_db
from ..database.orm import trade_type_dict
from ..utils import globals

def check_and_modify_balance(account_id, balance_change):
    return check_balance_and_raise(account_id, balance_change) 

def check_balance_and_trade(balance_decrease_agent_id:int, 
                            balance_increase_agent_id:int, 
                            trade_type:str, 
                            balance_change:int,
                            commodity_id: str,
                            from_user_name="Null",
                            to_user_name="Null" ,
                            ):
    try:
        balance_change = float(balance_change)
        assert balance_change > 0, f'the given price should be larger than 0, while the given price is {balance_change}'
        from_account_balance = check_and_modify_balance(balance_decrease_agent_id, -balance_change)
        to_account_balance = check_and_modify_balance(balance_increase_agent_id, balance_change)
        
        assert trade_type in trade_type_dict, f" {trade_type} is not a legal trady type. Legal trade type: {list(trade_type_dict.keys())}"
        if 'ARTWORK' in trade_type:
            update_artwork_in_db(artwork_id=commodity_id, request={"owner_id": balance_decrease_agent_id})
        
        add_trade_to_db(
        {
                "id": str(uuid.uuid4()),
                "type": trade_type_dict[trade_type],
                "from_agent_id":balance_decrease_agent_id,
                "to_agent_id": balance_increase_agent_id,
                "from_user_name": from_user_name,
                "to_user_name": to_user_name,
                "artwork_id": commodity_id,
                "amount": balance_change,
                "from_account_balance":from_account_balance ,
                "to_account_balance": to_account_balance,
                "desc": f"{trade_type} {commodity_id} from with price {balance_change}",
                "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "create_time_game": globals.date_num
            }
        )
        return {
                'success': 1,
                'from_account_balance': from_account_balance,
                'to_account_balance': to_account_balance,
            }
    except Exception as e:
        return {
            'success': 0, 
            'response': f'{e}', 
        }
        

def attr_modification(
    character: 'Character',
    attr: str,
    value: Union[int, float, str, Any],
    lower_bound: Union[int, float, str, Any],
    upper_bound: Union[int, float, str, Any],
):
    """
    modify the attribute of the character within the range of lower_bound and upper_bound. If the value is out of range, the attribute will be set to the nearest bound. The bound will be provided by the equipments.

    Args:
        character (Character): character object
        attr (str): attribute name
        value (Union[int, float, str, Any]): value to be modified
        lower_bound (Union[int, float, str, Any]): lower bound of the attribute
        upper_bound (Union[int, float, str, Any]): upper bound of the attribute
    """
    def update_mem_db(character, attr, value):
        update_agent_in_db(character.guid, {attr: value})
        setattr(character, attr, value)
        
    def _same_type_modification(character, attr, value, lower_bound, upper_bound):
        if type(value) == int and type(value) == float:
            value = type(getattr(character, attr))(value)
            if value < lower_bound:
                update_mem_db(character, attr, lower_bound)
            elif value > upper_bound:
                update_mem_db(character, attr, upper_bound)
            else:
                update_mem_db(character, attr, value)
        else:
            value = type(getattr(character, attr))(value)
            update_mem_db(character, attr, value)

    attr_type = type(getattr(character, attr))
    if type(value) == attr_type:
        _same_type_modification(character, attr, value, lower_bound, upper_bound)
    else:
        if attr_type == int or attr_type == float:
            try:
                value = attr_type(value)
                _same_type_modification(
                    character, attr, value, lower_bound, upper_bound
                )
            except:
                value = attr_type(random() * (upper_bound - lower_bound) + lower_bound)
                update_mem_db(character, attr, value)
        else:
            value = attr_type(value)
            update_mem_db(character, attr, value)
    