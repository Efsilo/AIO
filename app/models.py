from sqlalchemy import Column, String, Text, Float, DateTime
from app.database import Base
from datetime import datetime
import uuid

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)