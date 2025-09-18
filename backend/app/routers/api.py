from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..auth.deps import get_current_user
from ..usage.services import get_limits_for_user

router = APIRouter()

@router.get("/limits")
def my_limits(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_limits_for_user(db, user)
