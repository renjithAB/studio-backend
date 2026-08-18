from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_non_api_token
from app.models.users import User
from app.models.api_token import ApiToken
from app.schemas.api_token import ApiTokenCreate, ApiTokenResponse, ApiTokenWithPlaintext
from app.core.security import generate_api_token

router = APIRouter()

@router.get("/", response_model=List[ApiTokenResponse])
def list_api_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all active API tokens for the current user.
    """
    tokens = db.query(ApiToken).filter(
        ApiToken.user_id == current_user.id,
        ApiToken.is_active == True
    ).all()
    return tokens

@router.post("/", response_model=ApiTokenWithPlaintext, status_code=status.HTTP_201_CREATED)
def create_api_token(
    data: ApiTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: bool = Depends(require_non_api_token)  # Block API tokens from creating new API tokens
):
    """
    Create a new API token. The plain token is returned only once.
    """
    prefix, plain_token, hashed_token = generate_api_token()
    
    new_token = ApiToken(
        user_id=current_user.id,
        name=data.name,
        token_hash=hashed_token,
        prefix=prefix,
        is_active=True
    )
    
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    
    # We return the plain token so the user can copy it
    response = ApiTokenWithPlaintext.model_validate(new_token)
    response.token = plain_token
    return response

@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: bool = Depends(require_non_api_token)
):
    """
    Revoke an API token.
    """
    token = db.query(ApiToken).filter(
        ApiToken.id == token_id,
        ApiToken.user_id == current_user.id
    ).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
        
    db.delete(token)
    db.commit()
    return None
