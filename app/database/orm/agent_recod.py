from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from app.database.base_database import Base  # Ensure this imports correctly based on your project structure

class AgentRecord(Base):
    __tablename__ = 'agent'
    id = Column(String(255), primary_key=True)
    primitive = Column(Integer)
    character = Column(Integer)
    creativity = Column(Integer)
    charm = Column(Integer)
    art_style = Column(Integer)
    rebelliousness = Column(Integer)
    energy = Column(Integer)
    gold = Column(Integer)
    health = Column(Integer)