"""
init class for all repositories inheriting the base repository
"""
import logging
from functools import wraps

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, IntegrityError
from fastapi import status, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from typing import final, List, Optional
from ..repository.utils import check_duplicate_parameter
from sqlalchemy.inspection import inspect



from ..database.base_database import Base