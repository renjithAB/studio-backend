from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User

router = APIRouter()

class UserListItem(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True

@router.get("/list", response_model=List[UserListItem])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a lightweight list of all active users for dropdowns."""
    users = db.query(User).filter(
        User.is_active == True,
        User.is_deleted == False,
    ).order_by(User.first_name, User.last_name).all()
    return users
