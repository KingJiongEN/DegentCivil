from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from app.database.base_database import Base  # Ensure this imports correctly based on your project structure

class ArtworkRecord(Base):
    __tablename__ = 'artwork'
    id = Column(String(225), primary_key=True) # artwork_id / resource_id
    artwork_type = Column(String(255))
    resource = Column(String(255))
    owner_id = Column(String(255))
    owner_name = Column(String(255))
    prompt = Column(String(255))
    create_place_id = Column(String(255))
    create_place_name = Column(String(255))
    create_time_game = Column(Integer)
    create_time_real = Column(TIMESTAMP)
    price = Column(Integer)
    
