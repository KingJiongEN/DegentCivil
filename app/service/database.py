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


# 下面可以添加一些数据库操作的函数，例如创建、查询等
def create_town(session, town_data):
    """
    创建一个新的城镇记录
    :param session: 数据库会话
    :param town_data: 城镇数据
    :return: 新创建的城镇对象
    """
    # 示例代码，根据实际的模型结构进行调整
    new_town = Town(**town_data)
    session.add(new_town)
    session.commit()
    return new_town
