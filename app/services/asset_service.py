# app/services/asset_service.py
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.crud.crud_asset import asset as crud_asset
from app.schemas.asset import AssetCreate
from app.models.asset import Asset
from app.schemas.task import TaskCreate
from app.crud import task

class AssetService:
    
    @staticmethod
    def create_asset(
        db: Session,
        *,
        project_id: int,
        category_id: int,
        code: str,
        name: str,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        tag: Optional[str] = None,
        is_active: bool = True,
        created_by: int,
        tasks: Optional[List[str]] = None
    ) -> Asset:
        """Create a new asset with validation"""
        
        # Check if code already exists in this project
        existing = crud_asset.get_by_code(db, project_id=project_id, code=code)
        if existing:
            raise ValueError(f"Asset with code '{code}' already exists in this project")
        
        # Create asset
        asset_in = AssetCreate(
            code=code,
            name=name,
            project_id=project_id,
            category_id=category_id,
            description=description,
            thumbnail_url=thumbnail_url,
            tag=tag,
            is_active=is_active
        )
        
        new_asset = crud_asset.create(db, obj_in=asset_in, created_by=created_by)
        
        # 2. Create the Associated Tasks
        if tasks:
            for task_code in tasks:
                task_in_data = TaskCreate(
                    code=task_code,
                    # Fallback to capitalizing the code if you don't map it to a full name
                    name=task_code.capitalize(), 
                    project_id=project_id,
                    asset_id=new_asset.id,
                    is_active=True
                )
                
                # Create the task using your existing CRUD method
                task.create_task(db=db, task_in=task_in_data)
                
        return new_asset
    
    @staticmethod
    def get_assets_by_category(
        db: Session,
        *,
        project_id: int,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        return crud_asset.get_by_category(
            db, project_id=project_id, category_id=category_id, skip=skip, limit=limit
        )

asset_service = AssetService()