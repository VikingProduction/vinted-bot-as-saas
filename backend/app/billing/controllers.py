from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..auth.deps import get_current_user
from ..db import get_db
from ..models.user import User
from ..config import get_settings
from .services import create_checkout_session, create_billing_portal, upsert_subscription
import stripe

router = APIRouter()
settings = get_settings()

@router.post("/billing/checkout")
def start_checkout(price_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    host = request.headers.get("origin") or "http://localhost:3000"
    success_url = f"{host}/billing?status=success"
    cancel_url  = f"{host}/billing?status=cancel"
    url = create_checkout_session(user, price_id=price_id, success_url=success_url, cancel_url=cancel_url)
    return {"url": url}

@router.get("/billing/portal")
def billing_portal(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    host = request.headers.get("origin") or "http://localhost:3000"
    return {"url": create_billing_portal(user, return_url=f"{host}/billing")}

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not set")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    if event["type"] in ("customer.subscription.created", "customer.subscription.updated"):
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        from ..models.user import User
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            upsert_subscription(db, user, sub)
    return {"received": True}
