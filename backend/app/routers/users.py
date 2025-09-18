from fastapi import APIRouter, Depends, HTTPException
from ..models.user import User
from ..core.database import get_db
from sqlalchemy.orm import Session
from ..auth.auth_bearer import JWTBearer

router = APIRouter(tags=["users"], prefix="/users", dependencies=[Depends(JWTBearer())])

@router.get("/me")
def read_current_user(db: Session = Depends(get_db), token_data=Depends(JWTBearer())):
    user = db.query(User).filter(User.username == token_data["sub"]).first()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "subscription_plan": user.subscription_plan,
    }
