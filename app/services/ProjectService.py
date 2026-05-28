import os
import shutil
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json
from fastapi import UploadFile
from typing import Dict, List, Optional

from app.models.project import Project
from app.models.episode import Episode
from app.models.sequence import Sequence
from app.models.shot import Shot
from app.models.asset import Asset
from app.models.variant import Variant
from app.models.editorial import Editorial
from app.models.library import Library
from app.models.cycle import Cycle
from app.models.task import Task
from app.models.template import Template
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.domain import Domain
from app.models.category import Category
from app.models.publish_types import PublishType

# Configuration
UPLOAD_DIRECTORY = "uploads/projects/thumbnails"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

_CONFIG_PATH = Path(__file__).parent.parent / "core" / "template_config.json"
with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
    TEMPLATE_CONFIG = json.load(f)

from app.models.task_template import TaskTemplate, task_template_project_mappings

class ProjectService:
    
    @staticmethod
    async def save_thumbnail(file: UploadFile, project_code: str) -> str:
        upload_path = Path(UPLOAD_DIRECTORY)
        upload_path.mkdir(parents=True, exist_ok=True)
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type {file_ext} not allowed. Allowed types: {ALLOWED_EXTENSIONS}")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{project_code}_{unique_id}{file_ext}"
        file_path = upload_path / filename
        try:
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                raise ValueError(f"File size exceeds {MAX_FILE_SIZE//(1024*1024)}MB limit")
            with open(file_path, "wb") as f:
                f.write(contents)
            return f"/{UPLOAD_DIRECTORY}/{filename}"
        except Exception as e:
            raise Exception(f"Failed to save thumbnail: {str(e)}")

    @staticmethod
    def delete_thumbnail(thumbnail_url: str):
        if not thumbnail_url:
            return
        try:
            filename = Path(thumbnail_url).name
            file_path = Path(UPLOAD_DIRECTORY) / filename
            if file_path.exists():
                file_path.unlink()
                print(f"✓ Deleted thumbnail: {file_path}")
        except Exception as e:
            print(f"⚠ Failed to delete thumbnail: {str(e)}")

    # ---------- Main project creation ----------
    @staticmethod
    async def create_project_with_default_structure(
        db: Session,
        project_data: ProjectCreate,
        created_by: int,
        thumbnail_file: UploadFile = None
    ) -> Project:
        print(f"\n{'='*60}")
        print(f"CREATING PROJECT: {project_data.name} ({project_data.code})")
        print(f"{'='*60}")

        # 1. Handle thumbnail upload
        thumbnail_url = None
        if thumbnail_file:
            try:
                thumbnail_url = await ProjectService.save_thumbnail(thumbnail_file, project_data.code)
                print(f"✓ Thumbnail uploaded: {thumbnail_url}")
            except Exception as e:
                print(f"⚠ Thumbnail upload failed: {str(e)}")

        # 2. Create project
        project_dict = project_data.model_dump()
        project_dict['thumbnail_url'] = thumbnail_url
        project = Project(**project_dict, created_by=created_by, updated_by=created_by)
        db.add(project)
        db.flush()
        print(f"✓ Project created with ID: {project.id}")

        # 3. If no template, we're done
        if not project.template_id:
            print("⚠ No template_id provided, skipping default structure")
            db.commit()
            db.refresh(project)
            return project

        # 4. Retrieve the template record
        template = db.query(Template).filter(Template.id == project.template_id).first()
        if not template:
            print(f"⚠ Template {project.template_id} not found")
            db.commit()
            db.refresh(project)
            return project

        print(f"✓ Using template: {template.name} ({template.code})")
        template_code = template.code

        # 5. Determine which domains apply to this template
        # Episode domain only created for episodic templates; non-episodic get sequence instead
        applicable_domains = []
        for dom in TEMPLATE_CONFIG["domains"]:
            # Skip library and cycle on project creation
            if dom.get("code") in ["library", "cycle"]:
                continue
            # Episode domain: only include if template is episodic
            if dom.get("code") == "episode":
                if template.has_episode:
                    applicable_domains.append(dom)
                continue
            # Sequence domain: only include if template is NOT episodic
            if dom.get("code") == "sequence":
                if not template.has_episode:
                    applicable_domains.append(dom)
                continue
            if template_code in dom.get("applies_to_templates", []):
                applicable_domains.append(dom)
        print(f"Found {len(applicable_domains)} applicable domains (has_episode={template.has_episode})")

        # 6. Create Domain records
        domain_by_code: Dict[str, Domain] = {}
        for dom_def in applicable_domains:
            domain = Domain(
                code=dom_def["code"],
                name=dom_def["name"],
                description=dom_def.get("description"),
                project_id=project.id,
                created_by=created_by,
                updated_by=created_by,
                domain_type=dom_def["code"],
            )
            db.add(domain)
            db.flush()
            domain_by_code[dom_def["code"]] = domain
            print(f"✓ Created domain: {domain.code} (ID: {domain.id})")

        # 7. Create Categories under the Asset domain (if present)
        if "asset" in domain_by_code:
            asset_domain = domain_by_code["asset"]
            asset_categories = db.query(Template).filter(Template.tag == 'category', Template.is_active == True).all()
            for cat_tmpl in asset_categories:
                category = Category(
                    code=cat_tmpl.code,
                    name=cat_tmpl.name,
                    description=cat_tmpl.description,
                    domain_id=asset_domain.id,
                    project_id=project.id,
                    created_by=created_by,
                    updated_by=created_by,
                )
                db.add(category)
                db.flush()
                print(f"  ✓ Created category: {category.code} under Asset domain")

        # 8. Create hierarchy entities based on domains

        # Episode
        episode = None
        if "episode" in domain_by_code and template.has_episode:
            episode = Episode(
                code="EP01",
                name="Episode 01",
                description=f"Default episode for {project.name}",
                project_id=project.id,
                # domain_id=domain_by_code["episode"].id,
                created_by=created_by,
            )
            db.add(episode)
            db.flush()
            print(f"\n✓ CREATED EPISODE: {episode.code} (ID: {episode.id})")

        # Sequence
        # For episodic templates: sequence is under the episode
        # For non-episodic templates: sequence is at project level (no episode)
        sequence = None
        shots = []
        if template.has_episode and episode:
            # Episodic — create one default sequence under the episode
            sequence = Sequence(
                code="SQ01",
                name="Sequence 01",
                description=f"Default sequence for {project.name}",
                project_id=project.id,
                episode_id=episode.id,
                frame_start=1001,
                frame_end=1100,
                created_by=created_by,
            )
            db.add(sequence)
            db.flush()
            print(f"✓ CREATED SEQUENCE (under episode): {sequence.code} (ID: {sequence.id})")
        elif not template.has_episode and "sequence" in domain_by_code:
            # Non-episodic — create sequence directly at project level
            sequence = Sequence(
                code="SQ01",
                name="Sequence 01",
                description=f"Default sequence for {project.name}",
                project_id=project.id,
                episode_id=None,
                frame_start=1001,
                frame_end=1100,
                created_by=created_by,
            )
            db.add(sequence)
            db.flush()
            print(f"✓ CREATED SEQUENCE (project-level): {sequence.code} (ID: {sequence.id})")

        # Shots under the sequence (applies for both episodic and non-episodic paths)
        if sequence and "shot" in domain_by_code:
            shot_domain = domain_by_code["shot"]
            for i in range(1, 4):
                shot = Shot(
                    code=f"SH00{i}",
                    name=f"Shot 00{i}",
                    description=f"Default shot {i} for {project.name}",
                    project_id=project.id,
                    sequence_id=sequence.id,
                    frame_start=1001 + ((i-1) * 25),
                    frame_end=1001 + (i * 25) - 1,
                    asset_ids=[],
                    created_by=created_by,
                )
                db.add(shot)
                db.flush()
                shots.append(shot)
                print(f"  ✓ CREATED SHOT: {shot.code} (ID: {shot.id})")

        # Assets
        assets = []
        if "asset" in domain_by_code:
            asset_domain = domain_by_code["asset"]
            # Get all category IDs under this domain
            category_ids = db.query(Category.id).filter(
                Category.domain_id == asset_domain.id,
                Category.project_id == project.id
            ).limit(3).all()  # create up to 3 assets
            for (cat_id,) in category_ids:
                cat = db.get(Category, cat_id)
                asset = Asset(
                    code=f"{cat.code.upper()}_01",
                    name=f"Default {cat.name}",
                    description=f"Default {cat.name} asset for {project.name}",
                    project_id=project.id,
                    category_id=cat.id,
                    # domain_id=asset_domain.id,
                    created_by=created_by,
                )
                db.add(asset)
                db.flush()
                assets.append(asset)
                print(f"✓ CREATED ASSET: {asset.code} (ID: {asset.id}) (Category: {cat.name})")

                # Variant under this asset (if variant domain exists)
                if "variant" in domain_by_code:
                    variant = Variant(
                        code="default",
                        name="Default",
                        description=f"Default variant for {asset.name}",
                        project_id=project.id,
                        asset_id=asset.id,
                        # domain_id=domain_by_code["variant"].id,
                        created_by=created_by,
                    )
                    db.add(variant)
                    print(f"  ✓ CREATED VARIANT: {variant.code} for {asset.code}")

        # Editorial
        editorial = None
        if "editorial" in domain_by_code:
            editorial = Editorial(
                code="EDL01",
                name="Editorial 01",
                description=f"Default editorial for {project.name}",
                project_id=project.id,
                episode_id=episode.id if episode else None,
                # domain_id=domain_by_code["editorial"].id,
                created_by=created_by,
            )
            db.add(editorial)
            db.flush()
            print(f"✓ CREATED EDITORIAL: {editorial.code} (ID: {editorial.id})")

        # Library
        library = None
        # if "library" in domain_by_code:
        #     library = Library(
        #         code="LIB01",
        #         name="Library 01",
        #         description=f"Default library for {project.name}",
        #         project_id=project.id,
        #         # domain_id=domain_by_code["library"].id,
        #         created_by=created_by,
        #     )
        #     db.add(library)
        #     db.flush()
        #     print(f"✓ CREATED LIBRARY: {library.code} (ID: {library.id})")

        # Cycles
        cycles = []
        if "cycle" in domain_by_code and library:
            cycle_domain = domain_by_code["cycle"]
            for cycle_name in ['walk', 'run', 'idle']:
                cycle = Cycle(
                    code=cycle_name.upper(),
                    name=cycle_name.capitalize(),
                    description=f"Default {cycle_name} cycle",
                    project_id=project.id,
                    library_id=library.id,
                    # domain_id=cycle_domain.id,
                    created_by=created_by,
                )
                db.add(cycle)
                db.flush()
                cycles.append(cycle)
                print(f"  ✓ CREATED CYCLE: {cycle.code} (ID: {cycle.id})")

        # 9. Create Tasks from DB (task_templates table joined with project template)
        # Load task templates that apply to this project template
        task_definitions_db = (
            db.query(TaskTemplate)
            .join(
                task_template_project_mappings,
                TaskTemplate.id == task_template_project_mappings.c.task_template_id
            )
            .filter(task_template_project_mappings.c.project_template_id == template.id)
            .all()
        )
        print(f"Found {len(task_definitions_db)} task templates in DB for {template_code}")

        # Convert DB objects to same dict shape the loop below expects
        task_definitions = [
            {
                "code": t.code,
                "name": t.name,
                "description": t.description,
                "domain_code": t.domain_code.value if hasattr(t.domain_code, 'value') else t.domain_code,
                "applies_to_templates": [template_code],  # already filtered above
            }
            for t in task_definitions_db
        ]
        for task_def in task_definitions:
            if template_code not in task_def.get("applies_to_templates", []):
                continue
            domain_code = task_def.get("domain_code")
            if domain_code not in domain_by_code:
                continue

            # Determine parent entities based on domain_code
            if domain_code == "editorial" and editorial:
                task = Task(
                    code=task_def["code"],
                    name=task_def["name"],
                    description=task_def.get("description"),
                    project_id=project.id,
                    editorial_id=editorial.id,
                    # domain_id=domain_by_code[domain_code].id,
                    created_by=created_by,
                    updated_by=created_by,
                    is_active=True,
                )
                db.add(task)
                print(f"  ✓ CREATED TASK: {task.code} for Editorial")

            elif domain_code == "asset":
                for asset in assets:
                    task = Task(
                        code=task_def["code"],
                        name=task_def["name"],
                        description=task_def.get("description"),
                        project_id=project.id,
                        asset_id=asset.id,
                        # domain_id=domain_by_code[domain_code].id,
                        created_by=created_by,
                        updated_by=created_by,
                        is_active=True,
                    )
                    db.add(task)
                    print(f"  ✓ CREATED TASK: {task.code} for Asset {asset.code}")

            elif domain_code == "shot":
                for shot in shots:
                    task = Task(
                        code=task_def["code"],
                        name=task_def["name"],
                        description=task_def.get("description"),
                        project_id=project.id,
                        shot_id=shot.id,
                        # domain_id=domain_by_code[domain_code].id,
                        created_by=created_by,
                        updated_by=created_by,
                        is_active=True,
                    )
                    db.add(task)
                    print(f"  ✓ CREATED TASK: {task.code} for Shot {shot.code}")

            elif domain_code == "library" and library:
                task = Task(
                    code=task_def["code"],
                    name=task_def["name"],
                    description=task_def.get("description"),
                    project_id=project.id,
                    library_id=library.id,
                    # domain_id=domain_by_code[domain_code].id,
                    created_by=created_by,
                    updated_by=created_by,
                    is_active=True,
                )
                db.add(task)
                print(f"  ✓ CREATED TASK: {task.code} for Library")

            elif domain_code == "cycle":
                for cycle in cycles:
                    task = Task(
                        code=task_def["code"],
                        name=task_def["name"],
                        description=task_def.get("description"),
                        project_id=project.id,
                        cycle_id=cycle.id,
                        # domain_id=domain_by_code[domain_code].id,
                        created_by=created_by,
                        updated_by=created_by,
                        is_active=True,
                    )
                    db.add(task)
                    print(f"  ✓ CREATED TASK: {task.code} for Cycle {cycle.code}")

        # 10. Create Publish Types from DB (templates table, tag='publish')
        publish_definitions = (
            db.query(Template)
            .filter(Template.tag == "publish", Template.is_active == True)
            .order_by(Template.id)
            .all()
        )
        print(f"Found {len(publish_definitions)} publish type templates in DB")
        for pub_tmpl in publish_definitions:
            publish_type = PublishType(
                code=pub_tmpl.code,
                name=pub_tmpl.name,
                description=pub_tmpl.description,
                project_id=project.id,
                created_by=created_by,
                updated_by=created_by,
            )
            db.add(publish_type)
            print(f"  ✓ CREATED PUBLISH TYPE: {publish_type.code}")

        # 10. Commit everything
        db.commit()
        db.refresh(project)

        # 11. Verification
        print(f"\n{'='*60}")
        print("VERIFICATION:")
        print(f"  Domains: {db.query(Domain).filter(Domain.project_id == project.id).count()}")
        print(f"  Categories: {db.query(Category).filter(Category.project_id == project.id).count()}")
        print(f"  Episodes: {db.query(Episode).filter(Episode.project_id == project.id).count()}")
        print(f"  Sequences: {db.query(Sequence).filter(Sequence.project_id == project.id).count()}")
        print(f"  Shots: {db.query(Shot).filter(Shot.project_id == project.id).count()}")
        print(f"  Assets: {db.query(Asset).filter(Asset.project_id == project.id).count()}")
        print(f"  Variants: {db.query(Variant).filter(Variant.project_id == project.id).count()}")
        print(f"  Editorials: {db.query(Editorial).filter(Editorial.project_id == project.id).count()}")
        print(f"  Libraries: {db.query(Library).filter(Library.project_id == project.id).count()}")
        print(f"  Cycles: {db.query(Cycle).filter(Cycle.project_id == project.id).count()}")
        print(f"  Tasks: {db.query(Task).filter(Task.project_id == project.id).count()}")
        print(f"  Thumbnail: {project.thumbnail_url}")
        print(f"{'='*60}")

        return project
    
    @staticmethod
    async def update_project(
        db: Session, 
        db_obj: Project,
        obj_in: ProjectUpdate,
        updated_by: int,
        thumbnail_file: UploadFile = None
    ) -> Project:
        """Update project with optional thumbnail"""
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Handle thumbnail update
        if thumbnail_file:
            # Delete old thumbnail if exists
            if db_obj.thumbnail_url:
                ProjectService.delete_thumbnail(db_obj.thumbnail_url)
            
            # Save new thumbnail
            try:
                thumbnail_url = await ProjectService.save_thumbnail(
                    thumbnail_file, 
                    db_obj.code
                )
                update_data["thumbnail_url"] = thumbnail_url
                print(f"✓ Thumbnail updated: {thumbnail_url}")
            except Exception as e:
                print(f"⚠ Thumbnail update failed: {str(e)}")
        
        # Remove thumbnail if explicitly set to null
        if obj_in.thumbnail_url is None and db_obj.thumbnail_url:
            ProjectService.delete_thumbnail(db_obj.thumbnail_url)
            update_data["thumbnail_url"] = None
        
        update_data["updated_by"] = updated_by
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def delete_project(db: Session, project: Project):
        """Delete project and its thumbnail"""
        
        # Delete thumbnail if exists
        if project.thumbnail_url:
            ProjectService.delete_thumbnail(project.thumbnail_url)
        
        # Delete the project (cascade should handle related records)
        db.delete(project)
        db.commit()
        print(f"✓ Project {project.code} deleted")