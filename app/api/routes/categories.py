# app/api/routes/categories.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.auth.dependencies import get_current_user, get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, Category_response
from app.crud.crud_category import category as crud_category
from app.models.users import User
from app.models.category import Category
from sqlalchemy import cast, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.services.category import category_service
import logging
from app.schemas.asset import AssetOut
from app.models.asset import Asset

logger = logging.getLogger(__name__)
router = APIRouter()

# @router.get("/projects/{project_id}/categories", response_model=List[Category])
# def get_categories(
#     project_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     skip: int = 0,
#     limit: int = 100,
# ):
#     """
#     Get all categories for a project.
#     Categories are templates with tier='categoryTemplate'
#     """
#     categories = db.query(Template).filter(
#         Template.project_id == project_id,
#         Template.tier == "categoryTemplate",
#         Template.is_active == True
#     ).offset(skip).limit(limit).all()
    
#     return categories

@router.post("/templates/category", response_model=Category_response)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new category.
    Categories are stored in templates table with tier='categoryTemplate'
    """
    existing = db.query(Category).filter(
        Category.code == category_in.code,
        Category.project_id == category_in.project_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with code '{category_in.code}' already exists in this project"
        )
    
    category = category_service.create_category(
        db=db,
        category_in=category_in,
        created_by=current_user.id
    )
    
    return category

# @router.get("/categories/{category_id}", response_model=Category)
# def get_category(
#     category_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Get a specific category by ID
#     """
#     category = db.query(Template).filter(
#         Template.id == category_id,
#         Template.tier == "categoryTemplate"
#     ).first()
    
#     if not category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )
    
#     return category

# @router.put("/categories/{category_id}", response_model=Category)
# def update_category(
#     *,
#     db: Session = Depends(get_db),
#     category_id: int,
#     category_in: CategoryUpdate,
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Update a category
#     """
#     category = db.query(Template).filter(
#         Template.id == category_id,
#         Template.tier == "categoryTemplate"
#     ).first()
    
#     if not category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )
    
#     # Check permissions (only creator or superuser can update)
#     if category.created_by != current_user.id and not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
    
#     updated_category = category_service.update_category(
#         db=db,
#         db_obj=category,
#         category_in=category_in,
#         updated_by=current_user.id
#     )
    
#     return updated_category

# @router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_category(
#     *,
#     db: Session = Depends(get_db),
#     category_id: int,
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Soft delete a category
#     """
#     category = db.query(Template).filter(
#         Template.id == category_id,
#         Template.tier == "categoryTemplate"
#     ).first()
    
#     if not category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )
    
#     # Check permissions
#     if category.created_by != current_user.id and not current_user.is_superuser:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
    
#     # Check if category has assets
#     assets_count = db.query(Asset).filter(Asset.category_id == category_id).count()
#     if assets_count > 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Cannot delete category with {assets_count} assets. Delete or move assets first."
#         )
    
#     category.is_active = False
#     category.updated_by = current_user.id
#     db.commit()
    
#     return None

# @router.get("/categories/{category_id}/assets", response_model=List[AssetOut])
# def get_category_assets(
#     category_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     skip: int = 0,
#     limit: int = 100,
# ):
#     """
#     Get all assets in a category
#     """
#     # Verify category exists
#     category = db.query(Template).filter(
#         Template.id == category_id,
#         Template.tier == "categoryTemplate"
#     ).first()
    
#     if not category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )
    
#     assets = db.query(Asset).filter(
#         Asset.category_id == category_id,
#         Asset.is_active == True
#     ).offset(skip).limit(limit).all()
    
#     return assets

@router.put("/category/{category_id}", response_model=Category_response)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a category"""
    obj = crud_category.get(db, id=category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud_category.update(db, db_obj=obj, obj_in=data)