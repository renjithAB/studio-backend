import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.services.ProjectService import project_service
from app.models.project import Project
from app.models.users import User
from app.schemas.project import ProjectCreate

def fix_project(project_id: int):
    db = Session()
    
    try:
        # Get the project - now using integer ID directly
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            print(f"Project {project_id} not found")
            return
        
        print(f"Found project: {project.name} (ID: {project.id})")
        
        # Check if it already has data
        from app.models.episode import Episode
        episodes = db.query(Episode).filter(Episode.project_id == project.id).all()
        if episodes:
            print(f"Project already has {len(episodes)} episodes. Skipping.")
            return
        
        # Get admin user
        admin = db.query(User).filter(User.email == "test@test.com").first()
        if not admin:
            print("Admin user not found")
            return
        
        print(f"Found admin user: {admin.email} (ID: {admin.id})")
        
        # Create project data using the same logic
        project_service.create_project_with_default_structure(
            db=db,
            project_data=ProjectCreate(
                code=project.code,
                name=project.name,
                description=project.description,
                template_id=project.template_id
            ),
            created_by=admin.id
        )
        
        print("Project hierarchy created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Update this to use the integer ID of the project (from your new schema)
    # Example: project_id = 2000  # My Super Hero project
    project_id = 2000  # Update this with your actual project integer ID
    fix_project(project_id)