from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filter_id = Column(Integer, ForeignKey("vinted_filters.id"), nullable=False)
    vinted_item_id = Column(String(100), nullable=False)
    item_title = Column(String(500))
    item_price = Column(Float)
    item_url = Column(String(1000))
    action_taken = Column(
        Enum("alert", "sniped", "failed", name="action_enum"),
        default="alert",
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="alerts")
    filter = relationship("VintedFilter", back_populates="alerts")
