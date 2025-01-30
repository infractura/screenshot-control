"""Database models for screenshot service"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Screenshot(Base):
    """Screenshot history model"""
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    preset = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    full_page = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    image_data = Column(LargeBinary)
    thumbnail_data = Column(LargeBinary)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "preset": self.preset,
            "width": self.width,
            "height": self.height,
            "full_page": self.full_page,
            "created_at": self.created_at.isoformat(),
        }
