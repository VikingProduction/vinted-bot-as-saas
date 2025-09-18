# backend/app/routers/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from ..services.auth_service import authenticate_user, create_access_token
from ..models.user import User
from ..core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: dict, db: Session = Depends(get_db)):
    # user_in: {"email":..., "username":..., "password":...}
    existing = db.query(User).filter(
        (User.email == user_in["email"]) | (User.username == user_in["username"])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    user = User(
        email=user_in["email"],
        username=user_in["username"],
        hashed_password=user_in["password"],  # hashed in service
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "Inscription réussie"}
