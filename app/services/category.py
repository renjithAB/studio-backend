# app/services/category.py

from sqlalchemy.orm import Session
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, Category_response 
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    
    def create_category(
        self,
        db: Session,
        *,
        category_in: CategoryCreate,
        created_by: Optional[int] = None
    ) -> Category_response:
        """Create a new category (stored in templates table)"""
        
        logger.info(f"Creating category: {category_in.name} ({category_in.code})")
        
        db_obj = Category(
            code=category_in.code,
            name=category_in.name,
            project_id=category_in.project_id,
            domain_id = category_in.domain_id,
            description=category_in.description,
            is_active=category_in.is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"✓ Category created with ID: {db_obj.id}")
        
        # Convert back to response model (array -> single project_id)
        return db_obj
    
    # def update_category(
    #     self,
    #     db: Session,
    #     *,
    #     db_obj: Template,
    #     category_in: CategoryUpdate,
    #     updated_by: Optional[int] = None
    # ) -> Category:
    #     """Update a category"""
        
    #     update_data = category_in.model_dump(exclude_unset=True)
        
    #     # Handle project_id conversion if present
    #     if 'project_id' in update_data and update_data['project_id'] is not None:
    #         update_data['project_ids'] = [update_data['project_id']]
    #         del update_data['project_id']
        
    #     update_data["updated_by"] = updated_by
        
    #     for field, value in update_data.items():
    #         setattr(db_obj, field, value)
        
    #     db.commit()
    #     db.refresh(db_obj)
        
    #     logger.info(f"✓ Category updated: {db_obj.id}")
        
    #     # Convert back to response model
    #     return Category.from_orm_with_array(db_obj)

    # def get_category_by_code(
    #     self,
    #     db: Session,
    #     *,
    #     project_id: int,  # ✅ Changed from project_ids to project_id
    #     code: str
    # ) -> Optional[Template]:
    #     """Get a category by project ID and code"""
    #     return db.query(Template).filter(
    #         cast(Template.project_ids, JSONB).contains([project_id]),  # ✅ Use JSONB contains
    #         Template.code == code,
    #         Template.tier == "categoryTemplate",
    #         Template.is_active == True
    #     ).first()
    
    # def get_categories_by_project(
    #     self,
    #     db: Session,
    #     *,
    #     project_id: int,
    #     skip: int = 0,
    #     limit: int = 100
    # ) -> List[Category]:
    #     """Get all categories for a project"""
    #     templates = db.query(Template).filter(
    #         Template.tier == "categoryTemplate",
    #         Template.is_active == True,
    #         cast(Template.project_ids, JSONB).contains([project_id])
    #     ).offset(skip).limit(limit).all()
        
    #     # Convert each template to Category response model
    #     return [Category.from_orm_with_array(t) for t in templates]
    
    # def get_category_by_id(
    #     self,
    #     db: Session,
    #     *,
    #     category_id: int
    # ) -> Optional[Category]:
    #     """Get a category by ID"""
    #     template = db.query(Template).filter(
    #         Template.id == category_id,
    #         Template.tier == "categoryTemplate"
    #     ).first()
        
    #     if template:
    #         return Category.from_orm_with_array(template)
    #     return None
    
    # def delete_category(
    #     self,
    #     db: Session,
    #     *,
    #     category_id: int,
    #     updated_by: int
    # ) -> bool:
    #     """Soft delete a category"""
    #     template = db.query(Template).filter(
    #         Template.id == category_id,
    #         Template.tier == "categoryTemplate"
    #     ).first()
        
    #     if not template:
    #         return False
        
    #     template.is_active = False
    #     template.updated_by = updated_by
    #     db.commit()
        
    #     logger.info(f"✓ Category deleted: {category_id}")
    #     return True

category_service = CategoryService()