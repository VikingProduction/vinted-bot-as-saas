import stripe
from datetime import datetime
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.subscription import Subscription
from ..models.user import User

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

def ensure_stripe_customer(user: User) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(email=user.email)
    user.stripe_customer_id = customer["id"]
    return user.stripe_customer_id

def create_checkout_session(user: User, price_id: str, success_url: str, cancel_url: str):
    customer_id = ensure_stripe_customer(user)
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
    )
    return session["url"]

def create_billing_portal(user: User, return_url: str):
    customer_id = ensure_stripe_customer(user)
    portal = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    return portal["url"]

def upsert_subscription(db: Session, user: User, sub_obj: dict):
    stripe_sub_id = sub_obj["id"]
    status = sub_obj["status"]
    price = sub_obj["items"]["data"][0]["price"]
    plan_code = price.get("nickname") or price.get("lookup_key") or "unknown"
    current_period_end = datetime.fromtimestamp(sub_obj["current_period_end"])
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
    if not sub:
        sub = Subscription(
            user_id=user.id,
            stripe_subscription_id=stripe_sub_id,
            status=status,
            plan_code=plan_code,
            current_period_end=current_period_end,
        )
        db.add(sub)
    else:
        sub.status = status
        sub.plan_code = plan_code
        sub.current_period_end = current_period_end
    db.commit()
