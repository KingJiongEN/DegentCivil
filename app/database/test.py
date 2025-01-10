from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DDL

# Assuming the database `2` has already been created manually or through another process

# Database connection information
env_names = {
    'host': 'localhost',
    'port': '3306',
    'user': 'root',
    'password': '123456',
    'database_name': 'DgentCivil',
}

# Format the database connection string
db_connection_string = f"mysql+pymysql://{env_names['user']}:{env_names['password']}@{env_names['host']}:{env_names['port']}/{env_names['database_name']}"

# Create the SQLAlchemy engine
engine = create_engine(db_connection_string, echo=True, future=True)  # `echo=True` for verbose logging, `future=True` for SQLAlchemy 2.0 style

# Session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def init_db():
    # Ensure all models are imported here before calling init_db()
    # to make sure they are attached to the Base metadata.
    # Example: from yourapp import models
    Base.metadata.create_all(bind=engine)

# Example usage
if __name__ == "__main__":
    init_db()
