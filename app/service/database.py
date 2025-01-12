from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models.base import Base

# 定义数据库URL, 例如: "mysql+pymysql://user:password@localhost/dbname"
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 在需要时用于创建数据库表的函数
def create_tables():
    Base.metadata.create_all(bind=engine)


@contextmanager
def db_session():
    """提供一个事务性的数据库会话作用域"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

