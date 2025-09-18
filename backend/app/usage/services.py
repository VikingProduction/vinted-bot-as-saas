from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.subscription import Subscription
from ..models.user import User

settings = get_settings()

def get_user_plan_code(db: Session, user: User) -> str:
    sub = (
        db.query(Subscription)
          .filter(Subscription.user_id == user.id, Subscription.status.in_(["active", "trialing"]))
          .order_by(Subscription.id.desc())
          .first()
    )
    return sub.plan_code if sub else "free"

def get_limits_for_user(db: Session, user: User) -> dict:
    code = get_user_plan_code(db, user)
    return settings.PLAN_LIMITS.get(code, settings.PLAN_LIMITS["free"])
