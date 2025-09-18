# backend/app/routers/filters.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.filter import VintedFilter
from ..auth.auth_bearer import JWTBearer

router = APIRouter(tags=["filters"], prefix="/filters", dependencies=[Depends(JWTBearer())])

@router.post("/", response_model=dict)
def create_filter(payload: dict, db: Session = Depends(get_db), token_data=Depends(JWTBearer())):
    f = VintedFilter(user_id=token_data["user_id"], **payload)
    db.add(f)
    db.commit()
    db.refresh(f)
    return {"id": f.id, "msg": "Filtre créé"}

@router.get("/", response_model=List[dict])
def list_filters(db: Session = Depends(get_db), token_data=Depends(JWTBearer())):
    filters = db.query(VintedFilter).filter(VintedFilter.user_id == token_data["user_id"]).all()
    return [{"id": f.id, "name": f.name, "category": f.category} for f in filters]

@router.delete("/{filter_id}", status_code=204)
def delete_filter(filter_id: int, db: Session = Depends(get_db), token_data=Depends(JWTBearer())):
    f = db.query(VintedFilter).filter(
        VintedFilter.id == filter_id, VintedFilter.user_id == token_data["user_id"]
    ).first()
    if not f:
        raise HTTPException(404, "Filtre non trouvé")
    db.delete(f)
    db.commit()
