from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..db import Base

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, index=True)      # "free", "basic", "pro", "elite"
    stripe_price_id = Column(String(100), unique=True)       # price_xxx
    description = Column(String(255))

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stripe_subscription_id = Column(String(100), unique=True, index=True)
    plan_code = Column(String(50), index=True)
    status = Column(String(50), index=True)                  # active, trialing, canceled, past_due...
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="subscriptions")
