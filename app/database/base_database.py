import os
from sqlalchemy import create_engine
from sqlalchemy import DDL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from sqlalchemy.sql import text

from app.settings import db_connection_string
print(db_connection_string)

engine = create_engine(db_connection_string,echo=True, future=True )#connect_args={'sslmode': 'prefer'})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
event.listen(Base.metadata, 'before_create', DDL("CREATE DATABASE IF NOT EXISTS DgentCivil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
# event.listen(Base.metadata, 'before_create',)
from contextlib import contextmanager

@contextmanager
def get_db_context():
    try:
        db = next(get_db())  # Get the session object from the generator
        yield db
    finally:
        db.close()


def init_db():
    # import all modules before calling init_db()
    from app.database.orm import (
        artwork_record
    )
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
if __name__ == '__main__':
    init_db()
    print('Database initialized.')