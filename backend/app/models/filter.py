from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from ..core.database import Base

class VintedFilter(Base):
    __tablename__ = "vinted_filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    brand = Column(String(100))
    size = Column(String(50))
    color = Column(String(50))
    min_price = Column(Float)
    max_price = Column(Float)
    keywords = Column(String(500))
    snipping_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    user = relationship("User", back_populates="filters")
