from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.domain import Domain
from app.models.category import Category
from app.models.episode import Episode
from app.models.sequence import Sequence
from app.models.shot import Shot
from app.models.asset import Asset
from app.models.variant import Variant
from app.models.editorial import Editorial
from app.models.library import Library
from app.models.cycle import Cycle
from app.schemas.hierarchy import ProjectHierarchy, HierarchyEntity
from app.models.task import Task
from app.models.version import Version
from app.models.publish_types import PublishType
from sqlalchemy import inspect

class HierarchyService:
    
    @staticmethod
    def _get_model_data(obj: Any) -> Dict[str, Any]:
        """Dynamically extract all column values from a SQLAlchemy model instance."""
        if not obj:
            return {}
        try:
            # use inspect to get only true column attributes, avoiding relationships/internal state
            mapper = inspect(obj).mapper
            return {
                attr.key: getattr(obj, attr.key)
                for attr in mapper.column_attrs
            }
        except Exception:
            return {}

    @staticmethod
    def get_project_hierarchy(db: Session, project_id: int) -> Optional[ProjectHierarchy]:
        """Get complete project hierarchy based on existing domains and entities."""
        
        # 1. Get project
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.is_active == True
        ).first()
        if not project:
            return None
        
        project_code = project.code
        project_name = project.name
        
        # 2. Get all domains for this project – convert codes to UPPERCASE for consistent checks
        project_domains = db.query(Domain).filter(
            Domain.project_id == project_id,
            Domain.is_active == True
        ).all()

        domain_map = {
            (d.domain_type.value if hasattr(d.domain_type, 'value') else d.domain_type): d 
            for d in project_domains if d.domain_type
        }

        # domain_codes = [d.code.upper() for d in project_domains]          # ✅ uppercase list
        # domain_map = {d.code.upper(): d for d in project_domains}          # ✅ uppercase map
        
        # 3. Create root project node
        hierarchy = ProjectHierarchy(
            id=project.id,
            type="project",
            code=project.code,
            name=project.name,
            thumbnail_url=project.thumbnail_url,
            description=project.description,
            template_code=project.template.code if project.template else None,
            template_name=project.template.name if project.template else None,
            children=[],
            episode_count=0,
            asset_count=0,
            sequence_count=0,
            shot_count=0,
            editorial_count=0,
            library_count=0,
            cycle_count=0,
            task_count=0,
            variant_count=0,
            metadata={
                **HierarchyService._get_model_data(project),
                "template_id": project.template_id,
                "project_type": project.template.code if project.template else None
            }
        )
        
        header_id = -1  # negative IDs for headers
        
        # Check if project template is "Animation Feature Film" (code: "featurefilm")
        is_feature_film = False
        if project.template and (project.template.code == "featurefilm" or project.template.name == "Animation Feature Film"):
            is_feature_film = True

        if is_feature_film:
            # ==================== FEATURE FILM SEQUENCES SECTION ====================
            sequences_header = HierarchyEntity(
                id=-100,
                type="domain",
                domain_type='sequence',
                code="SEQUENCES",
                name="Sequences",
                description="All sequences in this project",
                children=[],
                metadata={
                    "domain_id": -100,
                    "can_create": True,
                    "create_type": "sequence"
                }
            )
            
            # Get actual sequences
            sequences = db.query(Sequence).filter(
                Sequence.project_id == project_id,
                Sequence.is_active == True
            ).order_by(Sequence.code).all()
            
            for sequence in sequences:
                sequence_node = HierarchyEntity(
                    id=sequence.id,
                    type="sequence",
                    code=sequence.code,
                    name=sequence.name,
                    thumbnail_url=sequence.thumbnail_url,
                    description=sequence.description,
                    children=[],
                    metadata={
                        **HierarchyService._get_model_data(sequence),
                        "domain_id": -100,
                        "project_id": sequence.project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "can_create": True,
                        "create_type": "shot"
                    }
                )
                
                # Get shots for this sequence
                shots = db.query(Shot).filter(
                    Shot.sequence_id == sequence.id,
                    Shot.is_active == True
                ).order_by(Shot.code).all()
                
                for shot in shots:
                    shot_node = HierarchyEntity(
                        id=shot.id,
                        type="shot",
                        domain_type="shot",
                        code=shot.code,
                        name=shot.name,
                        thumbnail_url=shot.thumbnail_url,
                        description=shot.description,
                        children=[],
                        metadata={
                            **HierarchyService._get_model_data(shot),
                            "domain_id": -100,
                            "domain_name": "Sequences",
                            "project_id": shot.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "episode_id": None,
                            "episode_code": None,
                            "episode_name": None,
                            "sequence_id": shot.sequence_id,
                            "sequence_code": sequence.code,
                            "sequence_name": sequence.name,
                            "can_create": True,
                            "create_type": "task"
                        }
                    )
                    hierarchy.shot_count += 1

                    # Get tasks for this shot
                    tasks = db.query(Task).filter(
                        Task.shot_id == shot.id,
                        Task.project_id == project_id,
                        Task.is_active == True
                    ).order_by(Task.code).all()

                    for task in tasks:
                        task_node = HierarchyEntity(
                            id=task.id,
                            type="task",
                            domain_type="task",
                            code=task.code,
                            name=task.name,
                            thumbnail_url=task.thumbnail_url,
                            description=task.description,
                            children=[],
                            metadata={
                                **HierarchyService._get_model_data(task),
                                "domain_id": -100,
                                "domain_name": "Sequences",
                                "project_id": task.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "episode_id": None,
                                "episode_code": None,
                                "episode_name": None,
                                "sequence_id": sequence.id,
                                "sequence_code": sequence.code,
                                "sequence_name": sequence.name,
                                "shot_id": task.shot_id,
                                "shot_code": shot.code,
                                "shot_name": shot.name,
                                "category_id": task.category_id,
                                "can_create": True,
                                "create_type": "publish"
                            }
                        )

                        publish_types = db.query(PublishType).filter(
                            PublishType.project_id == task.project_id,
                            PublishType.task_id == task.id
                        ).all()

                        for publish_type in publish_types:
                            pub_versions = db.query(Version).filter(
                                Version.publish_id == publish_type.id,
                                Version.is_active == True
                            ).order_by(Version.code).all()
                            version_nodes = []
                            for ver in pub_versions:
                                version_nodes.append(HierarchyEntity(
                                    id=ver.id,
                                    type="version",
                                    domain_type="version",
                                    code=ver.code,
                                    name=ver.name,
                                    description=ver.description,
                                    children=[],
                                    metadata={
                                        **HierarchyService._get_model_data(ver),
                                        "domain_id": -100,
                                        "project_id": task.project_id,
                                        "project_code": project_code,
                                        "episode_id": None,
                                        "episode_code": None,
                                        "sequence_id": sequence.id,
                                        "sequence_code": sequence.code,
                                        "shot_id": task.shot_id,
                                        "shot_code": shot.code,
                                        "task_id": task.id,
                                        "task_code": task.code,
                                        "publish_id": publish_type.id,
                                        "publish_code": publish_type.code,
                                    }
                                ))

                            publish_type_node = HierarchyEntity(
                                id=publish_type.id,
                                type="publish",
                                domain_type="publish",
                                code=publish_type.code,
                                name=publish_type.name,
                                description=publish_type.description,
                                children=version_nodes,
                                metadata={
                                    **HierarchyService._get_model_data(publish_type),
                                    "domain_id": -100,
                                    "domain_name": "Sequences",
                                    "project_id": task.project_id,
                                    "project_code": project_code,
                                    "project_name": project_name,
                                    "episode_id": None,
                                    "episode_code": None,
                                    "episode_name": None,
                                    "sequence_id": sequence.id,
                                    "sequence_code": sequence.code,
                                    "sequence_name": sequence.name,
                                    "shot_id": task.shot_id,
                                    "shot_code": shot.code,
                                    "shot_name": shot.name,
                                    "task_id": task.id,
                                    "task_code": task.code,
                                    "task_name": task.name,
                                    "can_create": True,
                                    "create_type": "version",
                                }
                            )
                            task_node.children.append(publish_type_node)

                        shot_node.children.append(task_node)
                    
                    sequence_node.children.append(shot_node)
                
                hierarchy.sequence_count += 1
                sequences_header.children.append(sequence_node)
            
            hierarchy.children.append(sequences_header)
        else:
            # ==================== EPISODES SECTION ====================
            episode_domain = domain_map.get('episode')
            if episode_domain:
                episodes_header = HierarchyEntity(
                    id=episode_domain.id,
                    type="domain",
                    domain_type='episode',
                    code="EPISODES",
                    name="Episodes",
                    description="All episodes in this project",
                    children=[],
                    metadata={
                        "domain_id": episode_domain.id,
                        "can_create": True,
                        "create_type": "episode"
                    }
                )
                header_id -= 1
                
                # Get actual episodes
                episodes = db.query(Episode).filter(
                    Episode.project_id == project_id,
                    Episode.is_active == True
                ).order_by(Episode.code).all()
                
                for episode in episodes:
                    episode_node = HierarchyEntity(
                        id=episode.id,
                        type="episode",
                        code=episode.code,
                        name=episode.name,
                        thumbnail_url=episode.thumbnail_url,
                        description=episode.description,
                        children=[],
                        metadata={
                            **HierarchyService._get_model_data(episode),
                            "domain_id": episode_domain.id,
                            "project_id": episode.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "can_create": True,
                            "create_type": "sequence"
                        }
                    )
                    
                    # Get sequences for this episode
                    sequences = db.query(Sequence).filter(
                        Sequence.episode_id == episode.id,
                        Sequence.is_active == True
                    ).order_by(Sequence.code).all()
                    
                    for sequence in sequences:
                        sequence_node = HierarchyEntity(
                            id=sequence.id,
                            type="sequence",
                            code=sequence.code,
                            name=sequence.name,
                            thumbnail_url=sequence.thumbnail_url,
                            description=sequence.description,
                            children=[],
                            metadata={
                                **HierarchyService._get_model_data(sequence),
                                "domain_id": episode_domain.id,
                                "project_id": sequence.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "episode_id": sequence.episode_id,
                                "episode_code": episode.code,
                                "episode_name": episode.name,
                                "can_create": True,
                                "create_type": "shot"
                            }
                        )
                        
                        # Get shots for this sequence
                        shots = db.query(Shot).filter(
                            Shot.sequence_id == sequence.id,
                            Shot.is_active == True
                        ).order_by(Shot.code).all()
                        
                        for shot in shots:
                            shot_node = HierarchyEntity(
                                id=shot.id,
                                type="shot",
                                domain_type="shot",
                                code=shot.code,
                                name=shot.name,
                                thumbnail_url=shot.thumbnail_url,
                                description=shot.description,
                                children=[],
                                metadata={
                                    **HierarchyService._get_model_data(shot),
                                    "domain_id": episode_domain.id,
                                    "domain_name": "Episodes",
                                    "project_id": shot.project_id,
                                    "project_code": project_code,
                                    "project_name": project_name,
                                    "episode_id": episode.id,
                                    "episode_code": episode.code,
                                    "episode_name": episode.name,
                                    "sequence_id": shot.sequence_id,
                                    "sequence_code": sequence.code,
                                    "sequence_name": sequence.name,
                                    "can_create": True,
                                    "create_type": "task"
                                }
                            )
                            hierarchy.shot_count += 1

                            # Get tasks for this shot
                            tasks = db.query(Task).filter(
                                Task.shot_id == shot.id,
                                Task.project_id == project_id,
                                Task.is_active == True
                            ).order_by(Task.code).all()

                            for task in tasks:
                                task_node = HierarchyEntity(
                                    id=task.id,
                                    type="task",
                                    domain_type="task",
                                    code=task.code,
                                    name=task.name,
                                    thumbnail_url=task.thumbnail_url,
                                    description=task.description,
                                    children=[],
                                    metadata={
                                        **HierarchyService._get_model_data(task),
                                        "domain_id": episode_domain.id,
                                        "domain_name": "Episodes",
                                        "project_id": task.project_id,
                                        "project_code": project_code,
                                        "project_name": project_name,
                                        "episode_id": episode.id,
                                        "episode_code": episode.code,
                                        "episode_name": episode.name,
                                        "sequence_id": sequence.id,
                                        "sequence_code": sequence.code,
                                        "sequence_name": sequence.name,
                                        "shot_id": task.shot_id,
                                        "shot_code": shot.code,
                                        "shot_name": shot.name,
                                        "category_id": task.category_id,
                                        "can_create": True,
                                        "create_type": "publish"
                                    }
                                )

                                publish_types = db.query(PublishType).filter(
                                    PublishType.project_id == task.project_id,
                                    PublishType.task_id == task.id
                                ).all()

                                for publish_type in publish_types:
                                    pub_versions = db.query(Version).filter(
                                        Version.publish_id == publish_type.id,
                                        Version.is_active == True
                                    ).order_by(Version.code).all()
                                    version_nodes = []
                                    for ver in pub_versions:
                                        version_nodes.append(HierarchyEntity(
                                            id=ver.id,
                                            type="version",
                                            domain_type="version",
                                            code=ver.code,
                                            name=ver.name,
                                            description=ver.description,
                                            children=[],
                                            metadata={
                                                **HierarchyService._get_model_data(ver),
                                                "domain_id": episode_domain.id,
                                                "project_id": task.project_id,
                                                "project_code": project_code,
                                                "episode_id": episode.id,
                                                "episode_code": episode.code,
                                                "sequence_id": sequence.id,
                                                "sequence_code": sequence.code,
                                                "shot_id": task.shot_id,
                                                "shot_code": shot.code,
                                                "task_id": task.id,
                                                "task_code": task.code,
                                                "publish_id": publish_type.id,
                                                "publish_code": publish_type.code,
                                            }
                                        ))

                                    publish_type_node = HierarchyEntity(
                                        id=publish_type.id,
                                        type="publish",
                                        domain_type="publish",
                                        code=publish_type.code,
                                        name=publish_type.name,
                                        description=publish_type.description,
                                        children=version_nodes,
                                        metadata={
                                            **HierarchyService._get_model_data(publish_type),
                                            "domain_id": episode_domain.id,
                                            "domain_name": "Episodes",
                                            "project_id": task.project_id,
                                            "project_code": project_code,
                                            "project_name": project_name,
                                            "episode_id": episode.id,
                                            "episode_code": episode.code,
                                            "episode_name": episode.name,
                                            "sequence_id": sequence.id,
                                            "sequence_code": sequence.code,
                                            "sequence_name": sequence.name,
                                            "shot_id": task.shot_id,
                                            "shot_code": shot.code,
                                            "shot_name": shot.name,
                                            "task_id": task.id,
                                            "task_code": task.code,
                                            "task_name": task.name,
                                            "can_create": True,
                                            "create_type": "version",
                                        }
                                    )
                                    task_node.children.append(publish_type_node)

                                shot_node.children.append(task_node)
                            
                            sequence_node.children.append(shot_node)
                        
                        hierarchy.sequence_count += 1
                        episode_node.children.append(sequence_node)
                    
                    episodes_header.children.append(episode_node)
                    hierarchy.episode_count += 1
                
                hierarchy.children.append(episodes_header)
        # ==================== ASSETS SECTION ====================
        asset_domain = domain_map.get('asset')
        if asset_domain:
            assets_header = HierarchyEntity(
                id=asset_domain.id,
                type="domain",
                domain_type='asset',
                code="ASSETS",
                name="Assets",
                description="All assets in this project",
                children=[],
                metadata={
                    **HierarchyService._get_model_data(asset_domain),
                    "domain_id": asset_domain.id,
                    "project_id": project_id,
                    "project_code": project_code,
                    "project_name": project_name,
                    "can_create": True,
                    "create_type": "category"
                }
            )

            categories = db.query(Category).filter(
                Category.domain_id == asset_domain.id,
                Category.project_id == project_id,
                Category.is_active == True
            ).order_by(Category.code).all()

            for category in categories:
                category_node = HierarchyEntity(
                    id=category.id,
                    type="category",
                    domain_type='asset',
                    code=category.code.upper(),
                    name=category.name,
                    thumbnail_url=category.thumbnail_url,
                    description=category.description or f"{category.name} assets",
                    children=[],
                    metadata={
                        **HierarchyService._get_model_data(category),
                        "category_id": category.id,
                        "category_name": category.name,
                        "category_code": category.code,
                        "domain_id": asset_domain.id,
                        "project_id": project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "can_create": True,
                        "create_type": "asset"
                    }
                )

                assets = db.query(Asset).filter(
                    Asset.project_id == project_id,
                    Asset.category_id == category.id,
                    Asset.is_active == True
                ).order_by(Asset.code).all()

                for asset in assets:
                    asset_node = HierarchyEntity(
                        id=asset.id,
                        type="asset",
                        domain_type='asset',
                        code=asset.code,
                        name=asset.name,
                        thumbnail_url=asset.thumbnail_url,
                        description=asset.description,
                        children=[],
                        metadata={
                            **HierarchyService._get_model_data(asset),
                            "domain_id": asset_domain.id,
                            "domain_name": "Assets",
                            "project_id": asset.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "category_id": asset.category_id,
                            "category_code": category.code,
                            "category_name": category.name,
                            "can_create": True,
                            "create_type": "task"
                        }
                    )

                    tasks = db.query(Task).filter(
                        Task.asset_id == asset.id,
                        Task.project_id == project_id,
                        Task.is_active == True
                    ).order_by(Task.code).all()

                    for task in tasks:
                        task_node = HierarchyEntity(
                            id=task.id,
                            type="task",
                            domain_type="task",
                            code=task.code,
                            name=task.name,
                            thumbnail_url=task.thumbnail_url,
                            description=task.description,
                            children=[],
                            metadata={
                                "domain_id": asset_domain.id,
                                "project_id": task.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "asset_id": task.asset_id,
                                "asset_code": asset.code,
                                "asset_name": asset.name,
                                "category_id": task.category_id,
                                "category_code": category.code,
                                "category_name": category.name,
                                "can_create": True,
                                "create_type": "variant"
                            }
                        )

                        variants = HierarchyService._get_reflected_variants(db, project_id, asset.id, task.id)

                        for variant in variants:
                            variant_node = HierarchyEntity(
                                id=variant.id,
                                type="variant",
                                domain_type="variant",
                                code=variant.code,
                                name=variant.name,
                                thumbnail_url=variant.thumbnail_url,
                                description=variant.description,
                                children=[],
                                metadata={
                                    **HierarchyService._get_model_data(variant),
                                    "domain_id": asset_domain.id,
                                    "domain_name": "Assets",
                                    "project_id": variant.project_id,
                                    "project_code": project_code,
                                    "project_name": project_name,
                                    "asset_id": variant.asset_id,
                                    "asset_code": asset.code,
                                    "asset_name": asset.name,
                                    "task_id": variant.task_id,
                                    "task_code": task.code,
                                    "task_name": task.name,
                                    "category_id": variant.category_id,
                                    "category_code": category.code,
                                    "category_name": category.name,
                                    "can_create": True,
                                    "create_type": "publish",
                                    "man_days": float(variant.man_days) if variant.man_days is not None else None,
                                    "start_at": variant.start_at,
                                    "end_at": variant.end_at,
                                    "priority": variant.priority,
                                    "assigned_by": variant.assigned_by,
                                    "review_by": variant.review_by,
                                    "status": variant.status
                                }
                            )

                            publish_types = HierarchyService._get_reflected_publishes(
                                db, project_id, variant.code, asset.id, variant.id
                            )

                            for publish_type in publish_types:
                                # Fetch version children for this publish type
                                pub_versions = db.query(Version).filter(
                                    Version.publish_id == publish_type.id,
                                    Version.is_active == True
                                ).order_by(Version.code).all()
                                version_nodes = []
                                for ver in pub_versions:
                                    version_nodes.append(HierarchyEntity(
                                        id=ver.id,
                                        type="version",
                                        domain_type="version",
                                        code=ver.code,
                                        name=ver.name,
                                        description=ver.description,
                                        children=[],
                                        metadata={
                                            **HierarchyService._get_model_data(ver),
                                            "domain_id": asset_domain.id,
                                            "project_id": variant.project_id,
                                            "project_code": project_code,
                                            "asset_id": variant.asset_id,
                                            "asset_code": asset.code,
                                            "task_id": variant.task_id,
                                            "task_code": task.code,
                                            "variant_id": variant.id,
                                            "variant_code": variant.code,
                                            "publish_id": publish_type.id,
                                            "publish_code": publish_type.code,
                                        }
                                    ))

                                publish_type_node = HierarchyEntity(
                                    id=publish_type.id,
                                    type="publish",
                                    domain_type="publish",
                                    code=publish_type.code,
                                    name=publish_type.name,
                                    description=publish_type.description,
                                    children=version_nodes,
                                    metadata={
                                        **HierarchyService._get_model_data(publish_type),
                                        "domain_id": asset_domain.id,
                                        "domain_name": "Assets",
                                        "project_id": variant.project_id,
                                        "project_code": project_code,
                                        "project_name": project_name,
                                        "asset_id": variant.asset_id,
                                        "asset_code": asset.code,
                                        "asset_name": asset.name,
                                        "task_id": variant.task_id,
                                        "task_code": task.code,
                                        "task_name": task.name,
                                        "variant_id": variant.id,
                                        "variant_code": variant.code,
                                        "variant_name": variant.name,
                                        "category_id": variant.category_id,
                                        "category_code": category.code,
                                        "category_name": category.name,
                                        "can_create": True,
                                        "create_type": "version",
                                    }
                                )
                                variant_node.children.append(publish_type_node)

                            task_node.children.append(variant_node)
                            hierarchy.variant_count += 1

                        asset_node.children.append(task_node)
                        hierarchy.task_count += 1

                    category_node.children.append(asset_node)
                    hierarchy.asset_count += 1

                assets_header.children.append(category_node)

            hierarchy.children.append(assets_header)
        # ==================== EDITORIALS SECTION ====================
        editorial_domain = domain_map.get('editorial')
        if editorial_domain:
            has_episode = project.template.has_episode if project.template else True
            
            if has_episode:
                editorials_header = HierarchyEntity(
                    id=editorial_domain.id,
                    type="domain",
                    domain_type='editorial',
                    code="EDITORIALS",
                    name="Editorials",
                    description="All editorials in this project",
                    children=[],
                    metadata={
                        "domain_id": editorial_domain.id,
                        "project_id": project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "can_create": True,
                        "create_type": "episode"
                    }
                )
                header_id -= 1
                
                episodes = db.query(Episode).filter(
                    Episode.project_id == project_id,
                    Episode.is_active == True
                ).order_by(Episode.code).all()
                
                for episode in episodes:
                    episode_node = HierarchyEntity(
                        id=episode.id,
                        type="episode",
                        code=episode.code,
                        name=episode.name,
                        thumbnail_url=episode.thumbnail_url,
                        description=episode.description,
                        children=[],
                        metadata={
                            "domain_id": editorial_domain.id,
                            "domain_type": "editorial",
                            "project_id": episode.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "can_create": True,
                            "create_type": "sequence"
                        }
                    )
                    
                    # Get sequences for this episode
                    sequences = db.query(Sequence).filter(
                        Sequence.episode_id == episode.id,
                        Sequence.is_active == True
                    ).order_by(Sequence.code).all()
                    
                    for sequence in sequences:
                        sequence_node = HierarchyEntity(
                            id=sequence.id,
                            type="sequence",
                            domain_type="editorial",
                            code=sequence.code,
                            name=sequence.name,
                            thumbnail_url=sequence.thumbnail_url,
                            description=sequence.description,
                            children=[],
                            metadata={
                                **HierarchyService._get_model_data(sequence),
                                "domain_id": editorial_domain.id,
                                "domain_type": "editorial",
                                "domain_name": "Editorials",
                                "project_id": sequence.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "episode_id": sequence.episode_id,
                                "episode_code": episode.code,
                                "episode_name": episode.name,
                                "can_create": True,
                                "create_type": "shot"
                            }
                        )
                        
                        # Get shots under sequence for this episode (editorial sequence has shots too)
                        shots = db.query(Shot).filter(
                            Shot.sequence_id == sequence.id,
                            Shot.project_id == project_id,
                            Shot.is_active == True
                        ).order_by(Shot.code).all()
                        
                        for shot in shots:
                            shot_node = HierarchyEntity(
                                id=shot.id,
                                type="shot",
                                domain_type="shot",
                                code=shot.code,
                                name=shot.name,
                                thumbnail_url=shot.thumbnail_url,
                                description=shot.description,
                                children=[],
                                metadata={
                                    "project_id": shot.project_id,
                                    "project_code": project_code,
                                    "project_name": project_name,
                                    "domain_id": editorial_domain.id,
                                    "domain_type": "editorial",
                                    "domain_name": "Editorials",
                                    "episode_id": episode.id,
                                    "episode_code": episode.code,
                                    "episode_name": episode.name,
                                    "sequence_id": sequence.id,
                                    "sequence_code": sequence.code,
                                    "sequence_name": sequence.name,
                                    "can_create": True,
                                    "create_type": "task"
                                }
                            )
                            
                            # Get tasks under this shot (editorial tasks only)
                            tasks = db.query(Task).filter(
                                Task.shot_id == shot.id,
                                Task.project_id == project_id,
                                Task.is_active == True
                            ).order_by(Task.code).all()
                            
                            for task in tasks:
                                task_node = HierarchyEntity(
                                    id=task.id,
                                    type="task",
                                    domain_type="task",
                                    code=task.code,
                                    name=task.name,
                                    thumbnail_url=task.thumbnail_url,
                                    description=task.description,
                                    children=[],
                                    metadata={
                                        "domain_id": editorial_domain.id,
                                        "domain_name": "Editorials",
                                        "project_id": task.project_id,
                                        "episode_id": episode.id,
                                        "episode_code": episode.code,
                                        "sequence_id": sequence.id,
                                        "sequence_code": sequence.code,
                                        "shot_id": shot.id,
                                        "shot_code": shot.code,
                                        "can_create": True,
                                        "create_type": "publish"
                                    }
                                )
                                
                                # Get publishes/versions for this task
                                publish_types = db.query(PublishType).filter(
                                    PublishType.project_id == task.project_id,
                                    PublishType.task_id == task.id
                                ).all()
                                
                                for publish_type in publish_types:
                                    pub_versions = db.query(Version).filter(
                                        Version.publish_id == publish_type.id,
                                        Version.is_active == True
                                    ).order_by(Version.code).all()
                                    
                                    version_nodes = []
                                    for ver in pub_versions:
                                        version_nodes.append(HierarchyEntity(
                                            id=ver.id,
                                            type="version",
                                            domain_type="version",
                                            code=ver.code,
                                            name=ver.name,
                                            description=ver.description,
                                            children=[],
                                            metadata={
                                                **HierarchyService._get_model_data(ver),
                                                "domain_id": editorial_domain.id,
                                                "project_id": task.project_id,
                                                "project_code": project_code,
                                                "episode_id": episode.id,
                                                "episode_code": episode.code,
                                                "sequence_id": sequence.id,
                                                "sequence_code": sequence.code,
                                                "task_id": task.id,
                                                "task_code": task.code,
                                                "publish_id": publish_type.id,
                                                "publish_code": publish_type.code,
                                            }
                                        ))
                                        
                                    publish_type_node = HierarchyEntity(
                                        id=publish_type.id,
                                        type="publish",
                                        domain_type="publish",
                                        code=publish_type.code,
                                        name=publish_type.name,
                                        description=publish_type.description,
                                        children=version_nodes,
                                        metadata={
                                            **HierarchyService._get_model_data(publish_type),
                                            "domain_id": editorial_domain.id,
                                            "domain_name": "Editorials",
                                            "project_id": task.project_id,
                                            "project_code": project_code,
                                            "project_name": project_name,
                                            "episode_id": episode.id,
                                            "episode_code": episode.code,
                                            "episode_name": episode.name,
                                            "sequence_id": sequence.id,
                                            "sequence_code": sequence.code,
                                            "sequence_name": sequence.name,
                                            "task_id": task.id,
                                            "task_code": task.code,
                                            "task_name": task.name,
                                            "can_create": True,
                                            "create_type": "version",
                                        }
                                    )
                                    task_node.children.append(publish_type_node)
                                    
                                shot_node.children.append(task_node)
                            sequence_node.children.append(shot_node)
                            
                        # Also support direct sequence editorial tasks if any legacy tasks exist
                        legacy_tasks = db.query(Task).filter(
                            Task.episode_id == episode.id,
                            Task.sequence_id == sequence.id,
                            Task.project_id == project_id,
                            Task.shot_id == None,
                            Task.is_active == True
                        ).order_by(Task.code).all()
                        for task in legacy_tasks:
                            task_node = HierarchyEntity(
                                id=task.id,
                                type="task",
                                domain_type="task",
                                code=task.code,
                                name=task.name,
                                thumbnail_url=task.thumbnail_url,
                                description=task.description,
                                children=[],
                                metadata={
                                    "domain_id": editorial_domain.id,
                                    "domain_name": "Editorials",
                                    "project_id": task.project_id,
                                    "episode_id": episode.id,
                                    "episode_code": episode.code,
                                    "sequence_id": sequence.id,
                                    "sequence_code": sequence.code,
                                    "shot_id": None,
                                    "can_create": True,
                                    "create_type": "publish"
                                }
                            )
                            # Get publishes/versions for this legacy task
                            publish_types = db.query(PublishType).filter(
                                PublishType.project_id == task.project_id,
                                PublishType.task_id == task.id
                            ).all()
                            for publish_type in publish_types:
                                pub_versions = db.query(Version).filter(
                                    Version.publish_id == publish_type.id,
                                    Version.is_active == True
                                ).order_by(Version.code).all()
                                version_nodes = []
                                for ver in pub_versions:
                                    version_nodes.append(HierarchyEntity(
                                        id=ver.id,
                                        type="version",
                                        domain_type="version",
                                        code=ver.code,
                                        name=ver.name,
                                        description=ver.description,
                                        children=[],
                                        metadata={
                                            **HierarchyService._get_model_data(ver),
                                            "domain_id": editorial_domain.id,
                                            "project_id": task.project_id,
                                            "project_code": project_code,
                                            "episode_id": episode.id,
                                            "episode_code": episode.code,
                                            "sequence_id": sequence.id,
                                            "sequence_code": sequence.code,
                                            "task_id": task.id,
                                            "task_code": task.code,
                                            "publish_id": publish_type.id,
                                            "publish_code": publish_type.code,
                                        }
                                    ))
                                publish_type_node = HierarchyEntity(
                                    id=publish_type.id,
                                    type="publish",
                                    domain_type="publish",
                                    code=publish_type.code,
                                    name=publish_type.name,
                                    description=publish_type.description,
                                    children=version_nodes,
                                    metadata={
                                        **HierarchyService._get_model_data(publish_type),
                                        "domain_id": editorial_domain.id,
                                        "domain_name": "Editorials",
                                        "project_id": task.project_id,
                                        "project_code": project_code,
                                        "project_name": project_name,
                                        "episode_id": episode.id,
                                        "episode_code": episode.code,
                                        "episode_name": episode.name,
                                        "sequence_id": sequence.id,
                                        "sequence_code": sequence.code,
                                        "sequence_name": sequence.name,
                                        "task_id": task.id,
                                        "task_code": task.code,
                                        "task_name": task.name,
                                        "can_create": True,
                                        "create_type": "version",
                                    }
                                )
                                task_node.children.append(publish_type_node)
                            sequence_node.children.append(task_node)
                            
                        episode_node.children.append(sequence_node)
                        
                    editorials_header.children.append(episode_node)
                    
                hierarchy.children.append(editorials_header)
            else:
                # Non-episodic project: Editorials -> Sequence -> Task -> Publish -> Version
                editorials_header = HierarchyEntity(
                    id=editorial_domain.id,
                    type="domain",
                    domain_type='editorial',
                    code="EDITORIALS",
                    name="Editorials",
                    description="All editorials in this project",
                    children=[],
                    metadata={
                        "domain_id": editorial_domain.id,
                        "domain_type": "editorial",
                        "project_id": project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "can_create": True,
                        "create_type": "sequence"
                    }
                )
                
                # Query all sequences directly under the project
                sequences = db.query(Sequence).filter(
                    Sequence.project_id == project_id,
                    Sequence.is_active == True
                ).order_by(Sequence.code).all()
                
                for sequence in sequences:
                    sequence_node = HierarchyEntity(
                        id=sequence.id,
                        type="sequence",
                        domain_type="editorial",
                        code=sequence.code,
                        name=sequence.name,
                        thumbnail_url=sequence.thumbnail_url,
                        description=sequence.description,
                        children=[],
                        metadata={
                            **HierarchyService._get_model_data(sequence),
                            "domain_id": editorial_domain.id,
                            "domain_type": "editorial",
                            "domain_name": "Editorials",
                            "project_id": sequence.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "episode_id": None,
                            "episode_code": None,
                            "episode_name": None,
                            "can_create": True,
                            "create_type": "shot"
                        }
                    )
                    
                    # Query shots under the sequence
                    shots = db.query(Shot).filter(
                        Shot.sequence_id == sequence.id,
                        Shot.project_id == project_id,
                        Shot.is_active == True
                    ).order_by(Shot.code).all()
                    
                    for shot in shots:
                        shot_node = HierarchyEntity(
                            id=shot.id,
                            type="shot",
                            domain_type="shot",
                            code=shot.code,
                            name=shot.name,
                            thumbnail_url=shot.thumbnail_url,
                            description=shot.description,
                            children=[],
                            metadata={
                                "project_id": shot.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "domain_id": editorial_domain.id,
                                "domain_type": "editorial",
                                "domain_name": "Editorials",
                                "episode_id": None,
                                "episode_code": None,
                                "episode_name": None,
                                "sequence_id": sequence.id,
                                "sequence_code": sequence.code,
                                "sequence_name": sequence.name,
                                "can_create": True,
                                "create_type": "task"
                            }
                        )
                        
                        # Get tasks under this shot (editorial tasks only)
                        tasks = db.query(Task).filter(
                            Task.shot_id == shot.id,
                            Task.project_id == project_id,
                            Task.is_active == True
                        ).order_by(Task.code).all()
                        
                        for task in tasks:
                            task_node = HierarchyEntity(
                                id=task.id,
                                type="task",
                                domain_type="task",
                                code=task.code,
                                name=task.name,
                                thumbnail_url=task.thumbnail_url,
                                description=task.description,
                                children=[],
                                metadata={
                                    "domain_id": editorial_domain.id,
                                    "domain_name": "Editorials",
                                    "project_id": task.project_id,
                                    "episode_id": None,
                                    "episode_code": None,
                                    "sequence_id": sequence.id,
                                    "sequence_code": sequence.code,
                                    "shot_id": shot.id,
                                    "shot_code": shot.code,
                                    "can_create": True,
                                    "create_type": "publish"
                                }
                            )
                            
                            # Get publishes and versions for this task
                            publish_types = db.query(PublishType).filter(
                                PublishType.project_id == task.project_id,
                                PublishType.task_id == task.id
                            ).all()
                            
                            for publish_type in publish_types:
                                pub_versions = db.query(Version).filter(
                                    Version.publish_id == publish_type.id,
                                    Version.is_active == True
                                ).order_by(Version.code).all()
                                
                                version_nodes = []
                                for ver in pub_versions:
                                    version_nodes.append(HierarchyEntity(
                                        id=ver.id,
                                        type="version",
                                        domain_type="version",
                                        code=ver.code,
                                        name=ver.name,
                                        description=ver.description,
                                        children=[],
                                        metadata={
                                            **HierarchyService._get_model_data(ver),
                                            "domain_id": editorial_domain.id,
                                            "project_id": task.project_id,
                                            "project_code": project_code,
                                            "episode_id": None,
                                            "episode_code": None,
                                            "sequence_id": sequence.id,
                                            "sequence_code": sequence.code,
                                            "task_id": task.id,
                                            "task_code": task.code,
                                            "publish_id": publish_type.id,
                                            "publish_code": publish_type.code,
                                        }
                                    ))
                                    
                                publish_type_node = HierarchyEntity(
                                    id=publish_type.id,
                                    type="publish",
                                    domain_type="publish",
                                    code=publish_type.code,
                                    name=publish_type.name,
                                    description=publish_type.description,
                                    children=version_nodes,
                                    metadata={
                                        **HierarchyService._get_model_data(publish_type),
                                        "domain_id": editorial_domain.id,
                                        "domain_name": "Editorials",
                                        "project_id": task.project_id,
                                        "project_code": project_code,
                                        "project_name": project_name,
                                        "episode_id": None,
                                        "episode_code": None,
                                        "episode_name": None,
                                        "sequence_id": sequence.id,
                                        "sequence_code": sequence.code,
                                        "sequence_name": sequence.name,
                                        "task_id": task.id,
                                        "task_code": task.code,
                                        "task_name": task.name,
                                        "can_create": True,
                                        "create_type": "version",
                                    }
                                )
                                task_node.children.append(publish_type_node)
                            shot_node.children.append(task_node)
                        sequence_node.children.append(shot_node)
                        
                    # Also support direct sequence editorial tasks if any legacy tasks exist
                    legacy_tasks = db.query(Task).filter(
                        Task.sequence_id == sequence.id,
                        Task.project_id == project_id,
                        Task.shot_id == None,
                        Task.is_active == True
                    ).order_by(Task.code).all()
                    for task in legacy_tasks:
                        task_node = HierarchyEntity(
                            id=task.id,
                            type="task",
                            domain_type="task",
                            code=task.code,
                            name=task.name,
                            thumbnail_url=task.thumbnail_url,
                            description=task.description,
                            children=[],
                            metadata={
                                "domain_id": editorial_domain.id,
                                "domain_name": "Editorials",
                                "project_id": task.project_id,
                                "episode_id": None,
                                "episode_code": None,
                                "sequence_id": sequence.id,
                                "sequence_code": sequence.code,
                                "shot_id": None,
                                "can_create": True,
                                "create_type": "publish"
                            }
                        )
                        # Get publishes/versions for this legacy task
                        publish_types = db.query(PublishType).filter(
                            PublishType.project_id == task.project_id,
                            PublishType.task_id == task.id
                        ).all()
                        for publish_type in publish_types:
                            pub_versions = db.query(Version).filter(
                                Version.publish_id == publish_type.id,
                                Version.is_active == True
                            ).order_by(Version.code).all()
                            version_nodes = []
                            for ver in pub_versions:
                                version_nodes.append(HierarchyEntity(
                                    id=ver.id,
                                    type="version",
                                    domain_type="version",
                                    code=ver.code,
                                    name=ver.name,
                                    description=ver.description,
                                    children=[],
                                    metadata={
                                        **HierarchyService._get_model_data(ver),
                                        "domain_id": editorial_domain.id,
                                        "project_id": task.project_id,
                                        "project_code": project_code,
                                        "episode_id": None,
                                        "episode_code": None,
                                        "sequence_id": sequence.id,
                                        "sequence_code": sequence.code,
                                        "task_id": task.id,
                                        "task_code": task.code,
                                        "publish_id": publish_type.id,
                                        "publish_code": publish_type.code,
                                    }
                                ))
                            publish_type_node = HierarchyEntity(
                                id=publish_type.id,
                                type="publish",
                                domain_type="publish",
                                code=publish_type.code,
                                name=publish_type.name,
                                description=publish_type.description,
                                children=version_nodes,
                                metadata={
                                    **HierarchyService._get_model_data(publish_type),
                                    "domain_id": editorial_domain.id,
                                    "domain_name": "Editorials",
                                    "project_id": task.project_id,
                                    "project_code": project_code,
                                    "project_name": project_name,
                                    "episode_id": None,
                                    "episode_code": None,
                                    "episode_name": None,
                                    "sequence_id": sequence.id,
                                    "sequence_code": sequence.code,
                                    "sequence_name": sequence.name,
                                    "task_id": task.id,
                                    "task_code": task.code,
                                    "task_name": task.name,
                                    "can_create": True,
                                    "create_type": "version",
                                }
                            )
                            task_node.children.append(publish_type_node)
                        sequence_node.children.append(task_node)
                    editorials_header.children.append(sequence_node)
                hierarchy.children.append(editorials_header)
        
        # ==================== LIBRARIES SECTION ====================
        library_domain = domain_map.get('library')
        if library_domain:
            libraries_header = HierarchyEntity(
                id=header_id,
                type="domain",
                domain_type='library',
                code="LIBRARIES",
                name="Libraries",
                description="All libraries in this project",
                children=[],
                metadata={
                    "domain_id": library_domain.id,
                    "project_id": project_id,
                    "project_code": project_code,
                    "project_name": project_name,
                    "can_create": True,
                    "create_type": "library"
                }
            )
            header_id -= 1
            
            libraries = db.query(Library).filter(
                Library.project_id == project_id,
                Library.is_active == True
            ).order_by(Library.code).all()
            
            for library in libraries:
                library_node = HierarchyEntity(
                    id=library.id,
                    type="library",
                    code=library.code,
                    name=library.name,
                    thumbnail_url=library.thumbnail_url,
                    description=library.description,
                    children=[],
                    metadata={
                        # "domain_id": library.domain_id,
                        "project_id": library.project_id,
                        "can_create": True,
                        "create_type": "cycle"
                    }
                )
                
                # Cycles under library
                cycle_domain = domain_map.get('CYCLE')
                if cycle_domain:
                    cycles = db.query(Cycle).filter(
                        Cycle.library_id == library.id,
                        Cycle.is_active == True
                    ).order_by(Cycle.code).all()
                    
                    if cycles:
                        cycles_header = HierarchyEntity(
                            id=header_id,
                            type="header",
                            code="CYCLES",
                            name="Cycles",
                            description=f"Cycles in {library.name}",
                            children=[],
                            metadata={
                                "domain_id": cycle_domain.id,
                                "can_create": True,
                                "create_type": "cycle"
                            }
                        )
                        
                        for cycle in cycles:
                            cycle_node = HierarchyEntity(
                                id=cycle.id,
                                type="cycle",
                                code=cycle.code,
                                name=cycle.name,
                                thumbnail_url=cycle.thumbnail_url,
                                description=cycle.description,
                                children=[],
                                metadata={
                                    # "domain_id": cycle.domain_id,
                                    "project_id": cycle.project_id,
                                    "library_id": cycle.library_id
                                }
                            )
                            cycles_header.children.append(cycle_node)
                            hierarchy.cycle_count += 1
                        
                        library_node.children.append(cycles_header)
                
                libraries_header.children.append(library_node)
                hierarchy.library_count += 1
            
            hierarchy.children.append(libraries_header)
        
        return hierarchy


    @staticmethod
    def get_entity_children(
        db: Session, 
        project_id: int, 
        entity_type: str, 
        entity_id: int,
        domain_type: Optional[str] = None
    ) -> List[HierarchyEntity]:
        """Fetch direct children for a specific entity type for lazy loading."""
        children = []

        project = db.query(Project).filter(Project.id == project_id).first()
        project_code = project.code if project else "UNK"
        project_name = project.name if project else "Unknown Project"

        is_feature_film = False
        if project and project.template and (project.template.code == "featurefilm" or project.template.name == "Animation Feature Film"):
            is_feature_film = True

        if entity_type == "project":
            # Project -> Domains
            domains = db.query(Domain).filter(
                Domain.project_id == project_id,
                Domain.is_active == True
            ).all()

            for d in domains:
                d_type = d.domain_type.value if hasattr(d.domain_type, 'value') else d.domain_type
                if is_feature_film and d_type == 'episode':
                    continue

                children.append(HierarchyEntity(
                    id=d.id,
                    type="domain",
                    domain_type=d_type,
                    code=d.code,
                    name=d.name,
                    thumbnail_url=d.thumbnail_url,
                    description=d.description,
                    children=[],
                    metadata={
                        "project_id": project_id,
                        "project_code": project_code,
                        "domain_id": d.id,
                        "can_create": True,
                        "create_type": "episode" if d_type in ['episode', 'editorial'] else ("category" if d_type == 'asset' else "library")
                    }
                ))

            if is_feature_film:
                children.append(HierarchyEntity(
                    id=-100,
                    type="domain",
                    domain_type='sequence',
                    code="SEQUENCES",
                    name="Sequences",
                    thumbnail_url=None,
                    description="All sequences in this project",
                    children=[],
                    metadata={
                        "project_id": project_id,
                        "project_code": project_code,
                        "domain_id": -100,
                        "can_create": True,
                        "create_type": "sequence"
                    }
                ))

        elif entity_type == "domain":
            # Domain -> Episodes, Categories, or Libraries
            if is_feature_film and entity_id == -100:
                sequences = db.query(Sequence).filter(
                    Sequence.project_id == project_id,
                    Sequence.is_active == True
                ).order_by(Sequence.code).all()

                for seq in sequences:
                    children.append(HierarchyEntity(
                        id=seq.id,
                        type="sequence",
                        code=seq.code,
                        name=seq.name,
                        thumbnail_url=seq.thumbnail_url,
                        description=seq.description,
                        children=[],
                        metadata={
                            "project_id": project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": -100,
                            "domain_name": "Sequences",
                            "episode_id": None,
                            "episode_code": None,
                            "episode_name": None,
                            "can_create": True,
                            "create_type": "shot"
                        }
                    ))
                return children

            domain = db.query(Domain).filter(Domain.id == entity_id).first()
            if not domain:
                return []
            
            domain_type = domain.domain_type.value if hasattr(domain.domain_type, 'value') else domain.domain_type

            if domain_type in ["episode", "editorial"]:
                has_episode = project.template.has_episode if project.template else True
                if domain_type == "editorial" and not has_episode:
                    # Non-episodic: load sequences directly under the editorial domain
                    sequences = db.query(Sequence).filter(
                        Sequence.project_id == project_id,
                        Sequence.is_active == True
                    ).order_by(Sequence.code).all()
                    
                    for seq in sequences:
                        children.append(HierarchyEntity(
                            id=seq.id,
                            type="sequence",
                            domain_type="editorial",
                            code=seq.code,
                            name=seq.name,
                            thumbnail_url=seq.thumbnail_url,
                            description=seq.description,
                            children=[],
                            metadata={
                                "domain_id": entity_id,
                                "domain_name": "Editorials",
                                "domain_type": "editorial",
                                "project_id": project_id,
                                "can_create": True,
                                "create_type": "shot"
                            }
                        ))
                    return children

                # Episodic projects (standard flow)
                episodes = db.query(Episode).filter(
                    Episode.project_id == project_id,
                    Episode.is_active == True
                ).order_by(Episode.code).all()

                for ep in episodes:
                    ep_node = HierarchyEntity(
                        id=ep.id,
                        type="episode",
                        code=ep.code,
                        name=ep.name,
                        thumbnail_url=ep.thumbnail_url,
                        description=ep.description,
                        children=[],
                        metadata={
                            "domain_id": entity_id,
                            "domain_type": domain_type,
                            "project_id": project_id,
                            "can_create": True,
                            "create_type": "sequence"
                        }
                    )
                    
                    # Pre-fetch sequences for this episode
                    sequences = db.query(Sequence).filter(
                        Sequence.episode_id == ep.id,
                        Sequence.project_id == project_id,
                        Sequence.is_active == True
                    ).order_by(Sequence.code).all()
                    
                    for seq in sequences:
                        ep_node.children.append(HierarchyEntity(
                            id=seq.id,
                            type="sequence",
                            domain_type=domain_type,
                            code=seq.code,
                            name=seq.name,
                            thumbnail_url=seq.thumbnail_url,
                            description=seq.description,
                            children=[],
                            metadata={
                                "project_id": project_id,
                                "episode_id": ep.id,
                                "domain_type": domain_type,
                                "can_create": True,
                                "create_type": "shot"
                            }
                        ))
                    
                    children.append(ep_node)
            
            elif domain_type == "asset":
                categories = db.query(Category).filter(
                    Category.domain_id == entity_id,
                    Category.project_id == project_id,
                    Category.is_active == True
                ).order_by(Category.code).all()

                for cat in categories:
                    children.append(HierarchyEntity(
                        id=cat.id,
                        type="category",
                        domain_type='asset',
                        code=cat.code,
                        name=cat.name,
                        thumbnail_url=cat.thumbnail_url,
                        description=cat.description,
                        children=[],
                        metadata={
                            "domain_id": entity_id,
                            "project_id": project_id,
                            "category_id": cat.id,
                            "can_create": True,
                            "create_type": "asset"
                        }
                    ))

            elif domain_type == "library":
                libraries = db.query(Library).filter(
                    Library.project_id == project_id,
                    Library.is_active == True
                ).order_by(Library.code).all()

                for lib in libraries:
                    children.append(HierarchyEntity(
                        id=lib.id,
                        type="library",
                        code=lib.code,
                        name=lib.name,
                        thumbnail_url=lib.thumbnail_url,
                        description=lib.description,
                        children=[],
                        metadata={
                            "project_id": project_id,
                            "can_create": True,
                            "create_type": "cycle"
                        }
                    ))

        elif entity_type == "episode":
            # 1. Fetch parent episode to get domain_id
            episode = db.query(Episode).filter(Episode.id == entity_id).first()
            
            # Find the episode or editorial domain for this project
            if domain_type:
                domain = db.query(Domain).filter(
                    Domain.project_id == project_id,
                    Domain.domain_type == domain_type.lower()
                ).first()
            else:
                domain = db.query(Domain).filter(
                    Domain.project_id == project_id,
                    Domain.domain_type.in_(['episode', 'editorial'])
                ).first()
            domain_id = domain.id if domain else None
            resolved_dom_type = domain.domain_type.value if domain and hasattr(domain.domain_type, 'value') else (domain.domain_type if domain else 'episode')

            sequences = db.query(Sequence).filter(
                Sequence.episode_id == entity_id,
                Sequence.project_id == project_id,
                Sequence.is_active == True
            ).order_by(Sequence.code).all()

            for seq in sequences:
                children.append(HierarchyEntity(
                    id=seq.id,
                    type="sequence",
                    domain_type=resolved_dom_type,
                    code=seq.code,
                    name=seq.name,
                    thumbnail_url=seq.thumbnail_url,
                    description=seq.description,
                    children=[],
                    metadata={
                        "project_id": seq.project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "domain_id": domain_id,
                        "domain_type": resolved_dom_type,
                        "domain_name": "Editorials" if resolved_dom_type == "editorial" else "Episodes",
                        "episode_id": seq.episode_id,
                        "episode_code": episode.code if episode else None,
                        "episode_name": episode.name if episode else None,
                        "can_create": True,
                        "create_type": "shot"
                    }
                ))

        elif entity_type == "sequence":
            # 1. Fetch sequence and its parent episode to get domain info
            sequence = db.query(Sequence).filter(Sequence.id == entity_id).first()
            episode = db.query(Episode).filter(Episode.id == sequence.episode_id).first() if sequence and sequence.episode_id else None
            if domain_type:
                domain_type = domain_type.lower()
                if domain_type == "editorials":
                    domain_type = "editorial"
                elif domain_type == "episodes":
                    domain_type = "episode"
                
                domain = db.query(Domain).filter(
                    Domain.project_id == project_id,
                    Domain.domain_type == domain_type
                ).first()
                domain_id = domain.id if domain else None
            else:
                domain = db.query(Domain).filter(
                    Domain.project_id == project_id,
                    Domain.domain_type.in_(['episode', 'editorial'])
                ).first() if sequence else None
                domain_type = domain.domain_type.value if domain and hasattr(domain.domain_type, 'value') else (domain.domain_type if domain else None)
                domain_id = domain.id if domain else None

            # Fetch shots under sequence in Episode, Editorial or featurefilm (Sequence-root) domain
            if domain_type in ['episode', 'editorial'] or is_feature_film:
                shots = db.query(Shot).filter(
                    Shot.sequence_id == entity_id,
                    Shot.project_id == project_id,
                    Shot.is_active == True
                ).order_by(Shot.code).all()

                for shot in shots:
                    # Determine virtual sequence header or correct domain
                    is_seq_root = is_feature_film and domain_type != 'editorial'
                    dom_id_to_use = -100 if is_seq_root else domain_id
                    dom_name_to_use = "Sequences" if is_seq_root else ("Editorials" if domain_type == 'editorial' else "Episodes")

                    shot_node = HierarchyEntity(
                        id=shot.id,
                        type="shot",
                        domain_type="shot",
                        code=shot.code,
                        name=shot.name,
                        thumbnail_url=shot.thumbnail_url,
                        description=shot.description,
                        children=[],
                        metadata={
                            "project_id": shot.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": dom_id_to_use,
                            "domain_name": dom_name_to_use,
                            "episode_id": None if is_seq_root else (sequence.episode_id if sequence else None),
                            "episode_code": None if is_seq_root else (episode.code if episode else None),
                            "episode_name": None if is_seq_root else (episode.name if episode else None),
                            "sequence_id": shot.sequence_id,
                            "sequence_code": sequence.code if sequence else None,
                            "sequence_name": sequence.name if sequence else None,
                            "can_create": True,
                            "create_type": "task"
                        }
                    )
                    
                    # Pre-fetch tasks for this shot
                    tasks = db.query(Task).filter(
                        Task.shot_id == shot.id,
                        Task.project_id == project_id,
                        Task.is_active == True
                    ).order_by(Task.code).all()
                    
                    for task in tasks:
                        shot_node.children.append(HierarchyEntity(
                            id=task.id,
                            type="task",
                            domain_type="task",
                            code=task.code,
                            name=task.name,
                            thumbnail_url=task.thumbnail_url,
                            description=task.description,
                            children=[],
                            metadata={
                                "project_id": task.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "domain_id": dom_id_to_use,
                                "domain_name": dom_name_to_use,
                                "episode_id": None if is_seq_root else (sequence.episode_id if sequence else None),
                                "episode_code": None if is_seq_root else (episode.code if episode else None),
                                "episode_name": None if is_seq_root else (episode.name if episode else None),
                                "sequence_id": sequence.id if sequence else None,
                                "sequence_code": sequence.code if sequence else None,
                                "sequence_name": sequence.name if sequence else None,
                                "shot_id": task.shot_id,
                                "shot_code": shot.code,
                                "shot_name": shot.name,
                                "can_create": True,
                                "create_type": "publish"
                            }
                        ))
                    
                    children.append(shot_node)
            
            # Fetch tasks if in Editorial domain, or if in episodic domain and we have no shots/children
            if domain_type == 'editorial' or (not is_feature_film and domain_type == 'episode' and not children):
                tasks = db.query(Task).filter(
                    Task.sequence_id == entity_id,
                    Task.project_id == project_id,
                    Task.shot_id == None,  # Ensure it is editorial task (directly under sequence)
                    Task.is_active == True
                ).order_by(Task.code).all()
                
                for task in tasks:
                    children.append(HierarchyEntity(
                        id=task.id,
                        type="task",
                        code=task.code,
                        name=task.name,
                        thumbnail_url=task.thumbnail_url,
                        description=task.description,
                        children=[],
                        metadata={
                            "project_id": task.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": domain_id,
                            "domain_name": domain.name if domain else "Episodes",
                            "episode_id": sequence.episode_id if sequence else None,
                            "episode_code": episode.code if episode else None,
                            "episode_name": episode.name if episode else None,
                            "sequence_id": task.sequence_id,
                            "sequence_code": sequence.code if sequence else None,
                            "sequence_name": sequence.name if sequence else None,
                            "can_create": True,
                            "create_type": "version"
                        }
                    ))

        elif entity_type == "shot":
            # 1. Traverse up to get episode/domain info
            shot = db.query(Shot).filter(Shot.id == entity_id).first()
            sequence = db.query(Sequence).filter(Sequence.id == shot.sequence_id).first() if shot else None
            episode = db.query(Episode).filter(Episode.id == sequence.episode_id).first() if sequence else None
            domain = db.query(Domain).filter(
                Domain.project_id == project_id,
                Domain.domain_type.in_(['episode', 'editorial'])
            ).first() if shot else None
            domain_id = domain.id if domain else None

            tasks = db.query(Task).filter(
                Task.shot_id == entity_id,
                Task.project_id == project_id,
                Task.is_active == True
            ).order_by(Task.code).all()

            for task in tasks:
                children.append(HierarchyEntity(
                    id=task.id,
                    type="task",
                    domain_type="task",
                    code=task.code,
                    name=task.name,
                    thumbnail_url=task.thumbnail_url,
                    description=task.description,
                    children=[],
                    metadata={
                        "project_id": task.project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "domain_id": domain_id,
                        "domain_name": "Episodes" if episode else None,
                        "episode_id": episode.id if episode else None,
                        "episode_code": episode.code if episode else None,
                        "episode_name": episode.name if episode else None,
                        "sequence_id": sequence.id if sequence else None,
                        "sequence_code": sequence.code if sequence else None,
                        "sequence_name": sequence.name if sequence else None,
                        "shot_id": task.shot_id,
                        "shot_code": shot.code if shot else None,
                        "shot_name": shot.name if shot else None,
                        "can_create": True,
                        "create_type": "publish"
                    }
                ))

        elif entity_type == "category":
            category = db.query(Category).filter(Category.id == entity_id).first()
            domain_id = category.domain_id if category else None

            assets = db.query(Asset).filter(
                Asset.category_id == entity_id,
                Asset.project_id == project_id,
                Asset.is_active == True
            ).order_by(Asset.code).all()

            for asset in assets:
                asset_node = HierarchyEntity(
                    id=asset.id,
                    type="asset",
                    domain_type="asset",
                    code=asset.code,
                    name=asset.name,
                    thumbnail_url=asset.thumbnail_url,
                    description=asset.description,
                    children=[],
                    metadata={
                        **HierarchyService._get_model_data(asset),
                        "project_id": asset.project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "domain_id": domain_id,
                        "domain_name": "Assets" if category else None,
                        "category_id": asset.category_id,
                        "category_code": category.code if category else None,
                        "category_name": category.name if category else None,
                        "can_create": True,
                        "create_type": "task"
                    }
                )
                
                # Fetch tasks for this asset
                tasks = db.query(Task).filter(
                    Task.asset_id == asset.id,
                    Task.project_id == project_id,
                    Task.is_active == True
                ).order_by(Task.code).all()
                
                for task in tasks:
                    task_node = HierarchyEntity(
                        id=task.id,
                        type="task",
                        domain_type="task",
                        code=task.code,
                        name=task.name,
                        thumbnail_url=task.thumbnail_url,
                        description=task.description,
                        children=[],
                        metadata={
                            **HierarchyService._get_model_data(task),
                            "project_id": task.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": domain_id,
                            "domain_name": "Assets",
                            "category_id": asset.category_id,
                            "category_code": category.code if category else None,
                            "category_name": category.name if category else None,
                            "asset_id": task.asset_id,
                            "asset_code": asset.code if asset else None,
                            "asset_name": asset.name if asset else None,
                            "can_create": True,
                            "create_type": "variant"
                        }
                    )

                    # Pre-fetch variants for this task (with reflection)
                    variants = HierarchyService._get_reflected_variants(db, project_id, asset.id, task.id)

                    for variant in variants:
                        task_node.children.append(HierarchyEntity(
                            id=variant.id,
                            type="variant",
                            domain_type="variant",
                            code=variant.code,
                            name=variant.name,
                            thumbnail_url=variant.thumbnail_url,
                            description=variant.description,
                            children=[],
                            metadata={
                                **HierarchyService._get_model_data(variant),
                                "project_id": variant.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "domain_id": domain_id,
                                "domain_name": "Assets",
                                "category_id": asset.category_id,
                                "asset_id": asset.id,
                                "task_id": task.id,
                                "can_create": True,
                                "create_type": "publish",
                                "man_days": float(variant.man_days) if variant.man_days is not None else None,
                                "start_at": variant.start_at,
                                "end_at": variant.end_at,
                                "priority": variant.priority,
                                "assigned_by": variant.assigned_by,
                                "review_by": variant.review_by,
                                "status": variant.status
                            }
                        ))
                    
                    asset_node.children.append(task_node)
                
                children.append(asset_node)

        elif entity_type == "asset":
            asset = db.query(Asset).filter(Asset.id == entity_id).first()
            category = db.query(Category).filter(Category.id == asset.category_id).first() if asset else None
            domain_id = category.domain_id if category else None

            tasks = db.query(Task).filter(
                Task.asset_id == entity_id,
                Task.project_id == project_id,
                Task.is_active == True
            ).order_by(Task.code).all()

            for task in tasks:
                task_node = HierarchyEntity(
                    id=task.id,
                    type="task",
                    domain_type="task",
                    code=task.code,
                    name=task.name,
                    thumbnail_url=task.thumbnail_url,
                    description=task.description,
                    children=[],
                    metadata={
                        **HierarchyService._get_model_data(task),
                        "project_id": task.project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "domain_id": domain_id,
                        "domain_name": "Assets" if category else None,
                        "category_id": category.id if category else None,
                        "category_code": category.code if category else None,
                        "category_name": category.name if category else None,
                        "asset_id": task.asset_id,
                        "asset_code": asset.code if asset else None,
                        "asset_name": asset.name if asset else None,
                        "can_create": True,
                        "create_type": "variant"
                    }
                )

                # Pre-fetch variants for this task (with reflection)
                variants = HierarchyService._get_reflected_variants(db, project_id, asset.id, task.id)

                for variant in variants:
                    task_node.children.append(HierarchyEntity(
                        id=variant.id,
                        type="variant",
                        domain_type="variant",
                        code=variant.code,
                        name=variant.name,
                        thumbnail_url=variant.thumbnail_url,
                        description=variant.description,
                        children=[],
                        metadata={
                            "project_id": variant.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": domain_id,
                            "domain_name": "Assets",
                            "category_id": category.id if category else None,
                            "asset_id": asset.id if asset else None,
                            "task_id": task.id,
                            "can_create": True,
                            "create_type": "publish",
                            "man_days": float(variant.man_days) if variant.man_days is not None else None,
                            "start_at": variant.start_at,
                            "end_at": variant.end_at,
                            "priority": variant.priority,
                            "assigned_by": variant.assigned_by,
                            "review_by": variant.review_by,
                            "status": variant.status
                        }
                    ))
                
                children.append(task_node)

        elif entity_type == "task":
            # Tasks could belong to an Asset OR a Shot, resolve domain_id accordingly
            task = db.query(Task).filter(Task.id == entity_id).first()
            domain_id = None
            category_id = getattr(task, 'category_id', None)
            asset_id = getattr(task, 'asset_id', None)
            
            if task:
                if task.asset_id:
                    asset = db.query(Asset).filter(Asset.id == task.asset_id).first()
                    cat = db.query(Category).filter(Category.id == asset.category_id).first() if asset else None
                    if cat: domain_id = cat.domain_id
                elif task.shot_id:
                    shot = db.query(Shot).filter(Shot.id == task.shot_id).first()
                    seq = db.query(Sequence).filter(Sequence.id == shot.sequence_id).first() if shot else None
                    domain = db.query(Domain).filter(
                        Domain.project_id == project_id,
                        Domain.domain_type.in_(['episode', 'editorial'])
                    ).first()
                    if domain: domain_id = domain.id

            # Fetch variants with reflection for asset tasks
            variants = HierarchyService._get_reflected_variants(db, project_id, asset_id, entity_id)

            if variants:
                # Optional: Pre-fetch asset and task info for metadata to improve performance
                curr_asset = db.query(Asset).filter(Asset.id == asset_id).first() if asset_id else None
                curr_task = db.query(Task).filter(Task.id == entity_id).first() if entity_id else None
                
                for variant in variants:
                    # Pre-fetch publish type children for this variant so they
                    # appear immediately without a separate expand call.
                    pub_children = HierarchyService._get_reflected_publishes(
                        db, variant.project_id, variant.code, asset_id, variant.id
                    )
                    pub_nodes = []
                    for pub in pub_children:
                        # Pre-fetch version children for each publish type
                        pub_versions = db.query(Version).filter(
                            Version.publish_id == pub.id,
                            Version.is_active == True
                        ).order_by(Version.code).all()
                        version_nodes = []
                        for ver in pub_versions:
                            version_nodes.append(HierarchyEntity(
                                id=ver.id,
                                type="version",
                                domain_type="version",
                                code=ver.code,
                                name=ver.name,
                                description=ver.description,
                                children=[],
                        metadata={
                            **HierarchyService._get_model_data(ver),
                            "project_id": variant.project_id,
                            "domain_id": domain_id,
                            "asset_id": asset_id,
                            "task_id": entity_id,
                            "task_code": curr_task.code if curr_task else None,
                            "variant_id": variant.id,
                            "variant_code": variant.code,
                            "publish_id": pub.id,
                            "publish_code": pub.code,
                        }
                            ))

                        pub_nodes.append(HierarchyEntity(
                            id=pub.id,
                            type="publish",
                            domain_type="publish",
                            code=pub.code,
                            name=pub.name,
                            description=pub.description,
                            children=version_nodes,
                            metadata={
                                **HierarchyService._get_model_data(pub),
                                "project_id": variant.project_id,
                                "project_code": project_code,
                                "project_name": project_name,
                                "domain_id": domain_id,
                                "asset_id": asset_id,
                                "asset_code": curr_asset.code if curr_asset else None,
                                "asset_name": curr_asset.name if curr_asset else None,
                                "task_id": entity_id,
                                "task_code": curr_task.code if curr_task else None,
                                "task_name": curr_task.name if curr_task else None,
                                "variant_id": variant.id,
                                "variant_code": variant.code,
                                "variant_name": variant.name,
                                "can_create": True,
                                "create_type": "version",
                            }
                        ))

                    children.append(HierarchyEntity(
                        id=variant.id,
                        type="variant",
                        domain_type="variant",
                        code=variant.code,
                        name=variant.name,
                        thumbnail_url=variant.thumbnail_url,
                        description=variant.description,
                        children=pub_nodes,
                        metadata={
                            **HierarchyService._get_model_data(variant),
                            "project_id": variant.project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": domain_id,
                            "domain_name": "Assets",
                            "category_id": category_id,
                            "asset_id": asset_id,
                            "asset_code": curr_asset.code if curr_asset else None,
                            "asset_name": curr_asset.name if curr_asset else None,
                            "task_id": entity_id,
                            "task_code": curr_task.code if curr_task else None,
                            "task_name": curr_task.name if curr_task else None,
                            "can_create": True,
                            "create_type": "publish",
                            "man_days": float(variant.man_days) if variant.man_days is not None else None,
                            "start_at": variant.start_at,
                            "end_at": variant.end_at,
                            "priority": variant.priority,
                            "assigned_by": variant.assigned_by,
                            "review_by": variant.review_by,
                            "status": variant.status
                        }
                    ))
            else:
                publishes = db.query(PublishType).filter(
                    PublishType.project_id == project_id,
                    PublishType.task_id == entity_id
                ).all()

                for pub in publishes:
                    pub_versions = db.query(Version).filter(
                        Version.publish_id == pub.id,
                        Version.is_active == True
                    ).order_by(Version.code).all()
                    version_nodes = []
                    for ver in pub_versions:
                        version_nodes.append(HierarchyEntity(
                            id=ver.id,
                            type="version",
                            domain_type="version",
                            code=ver.code,
                            name=ver.name,
                            description=ver.description,
                            children=[],
                            metadata={
                                **HierarchyService._get_model_data(ver),
                                "project_id": project_id,
                                "domain_id": domain_id,
                                "task_id": entity_id,
                                "task_code": task.code if task else None,
                                "shot_id": task.shot_id if task else None,
                                "shot_code": db.query(Shot).filter(Shot.id == task.shot_id).first().code if task and task.shot_id else None,
                                "episode_id": task.episode_id if task else None,
                                "sequence_id": task.sequence_id if task else None,
                                "publish_id": pub.id,
                                "publish_code": pub.code,
                            }
                        ))

                    children.append(HierarchyEntity(
                        id=pub.id,
                        type="publish",
                        domain_type="publish",
                        code=pub.code,
                        name=pub.name,
                        description=pub.description,
                        children=version_nodes,
                        metadata={
                            **HierarchyService._get_model_data(pub),
                            "project_id": project_id,
                            "project_code": project_code,
                            "project_name": project_name,
                            "domain_id": domain_id,
                            "task_id": entity_id,
                            "task_code": task.code if task else None,
                            "task_name": task.name if task else None,
                            "asset_id": task.asset_id if task else None,
                            "asset_code": db.query(Asset).filter(Asset.id == task.asset_id).first().code if task and task.asset_id else None,
                            "asset_name": db.query(Asset).filter(Asset.id == task.asset_id).first().name if task and task.asset_id else None,
                            "shot_id": task.shot_id if task else None,
                            "shot_code": db.query(Shot).filter(Shot.id == task.shot_id).first().code if task and task.shot_id else None,
                            "shot_name": db.query(Shot).filter(Shot.id == task.shot_id).first().name if task and task.shot_id else None,
                            "episode_id": task.episode_id if task else None,
                            "sequence_id": task.sequence_id if task else None,
                            "can_create": True,
                            "create_type": "version",
                        }
                    ))

        elif entity_type == "variant":
            # Variant -> Publishes
            variant = db.query(Variant).filter(Variant.id == entity_id).first()
            task = db.query(Task).filter(Task.id == variant.task_id).first() if variant else None
            
            # Resolve domain_id (similar to task case)
            domain_id = None
            if task:
                if task.asset_id:
                    asset = db.query(Asset).filter(Asset.id == task.asset_id).first()
                    cat = db.query(Category).filter(Category.id == asset.category_id).first() if asset else None
                    if cat: domain_id = cat.domain_id
                elif task.shot_id:
                    shot = db.query(Shot).filter(Shot.id == task.shot_id).first()
                    seq = db.query(Sequence).filter(Sequence.id == shot.sequence_id).first() if shot else None
                    domain = db.query(Domain).filter(
                        Domain.project_id == project_id,
                        Domain.domain_type.in_(['episode', 'editorial'])
                    ).first()
                    if domain: domain_id = domain.id

            publishes = HierarchyService._get_reflected_publishes(
                db, project_id, variant.code if variant else None, task.asset_id if task else None, entity_id
            )

            for pub in publishes:
                # Pre-fetch version children for this publish type
                pub_versions = db.query(Version).filter(
                    Version.publish_id == pub.id,
                    Version.is_active == True
                ).order_by(Version.code).all()
                version_nodes = []
                for ver in pub_versions:
                    version_nodes.append(HierarchyEntity(
                        id=ver.id,
                        type="version",
                        domain_type="version",
                        code=ver.code,
                        name=ver.name,
                        description=ver.description,
                        children=[],
                        metadata={
                            **HierarchyService._get_model_data(ver),
                            "project_id": project_id,
                            "domain_id": domain_id,
                            "task_id": task.id if task else None,
                            "task_code": task.code if task else None,
                            "variant_id": entity_id,
                            "variant_code": variant.code if variant else None,
                            "asset_id": task.asset_id if task else None,
                            "publish_id": pub.id,
                            "publish_code": pub.code,
                        }
                    ))

                children.append(HierarchyEntity(
                    id=pub.id,
                    type="publish",
                    domain_type="publish",
                    code=pub.code,
                    name=pub.name,
                    description=pub.description,
                    children=version_nodes,
                    metadata={
                        "project_id": project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "domain_id": domain_id,
                        "task_id": task.id if task else None,
                        "task_code": task.code if task else None,
                        "task_name": task.name if task else None,
                        "variant_id": entity_id,
                        "variant_code": variant.code if variant else None,
                        "variant_name": variant.name if variant else None,
                        "asset_id": task.asset_id if task else None,
                        "asset_code": db.query(Asset).filter(Asset.id == task.asset_id).first().code if task and task.asset_id else None,
                        "asset_name": db.query(Asset).filter(Asset.id == task.asset_id).first().name if task and task.asset_id else None,
                        "can_create": True,
                        "create_type": "version",
                    }
                ))

        elif entity_type == "publish":
            # Publish type -> Versions
            pub = db.query(PublishType).filter(PublishType.id == entity_id).first()
            variant = db.query(Variant).filter(Variant.id == pub.variant_id).first() if pub and pub.variant_id else None
            task = db.query(Task).filter(Task.id == pub.task_id).first() if pub and pub.task_id else None

            versions = db.query(Version).filter(
                Version.publish_id == entity_id,
                Version.is_active == True
            ).order_by(Version.code).all()

            for ver in versions:
                children.append(HierarchyEntity(
                    id=ver.id,
                    type="version",
                    domain_type="version",
                    code=ver.code,
                    name=ver.name,
                    description=ver.description,
                    children=[],
                    metadata={
                        "project_id": project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "task_id": task.id if task else None,
                        "task_code": task.code if task else None,
                        "task_name": task.name if task else None,
                        "variant_id": variant.id if variant else None,
                        "variant_code": variant.code if variant else None,
                        "asset_id": task.asset_id if task else None,
                        "publish_id": entity_id,
                        "publish_code": pub.code if pub else None,
                        "episode_id": task.episode_id if task else None,
                        "sequence_id": task.sequence_id if task else None,
                        "shot_id": task.shot_id if task else None,
                    }
                ))

        elif entity_type == "library":
            # Library -> Cycles
            cycles = db.query(Cycle).filter(
                Cycle.library_id == entity_id,
                Cycle.project_id == project_id,
                Cycle.is_active == True
            ).order_by(Cycle.code).all()

            for cycle in cycles:
                children.append(HierarchyEntity(
                    id=cycle.id,
                    type="cycle",
                    code=cycle.code,
                    name=cycle.name,
                    thumbnail_url=cycle.thumbnail_url,
                    description=cycle.description,
                    children=[],
                    metadata={
                        **HierarchyService._get_model_data(cycle),
                        "project_id": cycle.project_id,
                        "project_code": project_code,
                        "project_name": project_name,
                        "library_id": cycle.library_id
                    }
                ))

        return children

    @staticmethod
    def _get_reflected_variants(db: Session, project_id: int, asset_id: Optional[int], task_id: int) -> List[Variant]:
        """Fetch reflected variants for a task. If asset_id is provided, returns variants from all tasks in asset,
        de-duplicated by NAME (since each row now has a unique code but shared name identifies the logical variant)."""
        if asset_id:
            db.expire_all()

            variants_raw = db.query(Variant).filter(
                Variant.asset_id == asset_id,
                Variant.is_active == True
            ).order_by(Variant.name, Variant.id).all()

            # De-duplicate by name, preferring current task's record
            variants_map = {}
            for v in variants_raw:
                key = (v.name or "").lower()
                if key not in variants_map or v.task_id == task_id:
                    variants_map[key] = v
            return sorted(variants_map.values(), key=lambda x: (x.name or "").lower())
        else:
            # Regular task (shot task), only return its own variants
            return db.query(Variant).filter(
                Variant.task_id == task_id,
                Variant.project_id == project_id,
                Variant.is_active == True
            ).order_by(Variant.code).all()

    @staticmethod
    def _get_reflected_publishes(db: Session, project_id: int, variant_code: Optional[str], asset_id: Optional[int], variant_id: int) -> List[PublishType]:
        """Fetch reflected publish types for a variant. Returns publishes linked to any variant
        that shares the same NAME as the given variant (since codes are now unique per row)."""
        if asset_id:
            db.expire_all()

            # Find the name of the given variant
            base_variant = db.query(Variant).filter(Variant.id == variant_id).first()
            variant_name = (base_variant.name or "").lower() if base_variant else None

            if not variant_name:
                return []

            # Find all variants across the asset with the same name
            variant_ids_query = db.query(Variant.id).filter(
                Variant.asset_id == asset_id,
                Variant.name.ilike(variant_name),
                Variant.is_active == True
            ).all()
            variant_ids_list = [v.id for v in variant_ids_query]

            if not variant_ids_list:
                return []

            # Fetch ALL publishes for these variants
            # We remove the project_id filter here because publishers should be visible
            # across the asset context regardless of individual record project_id drift.
            pub_raw = db.query(PublishType).filter(
                PublishType.variant_id.in_(variant_ids_list)
            ).order_by(PublishType.code).all()

            # De-duplicate by code, preferring current variant's record if possible
            pub_map = {}
            for p in pub_raw:
                if p.code not in pub_map or p.variant_id == variant_id:
                    pub_map[p.code] = p
            return sorted(pub_map.values(), key=lambda x: x.code)
        else:
            # Regular variant child fetch (non-asset or missing info)
            return db.query(PublishType).filter(
                PublishType.variant_id == variant_id,
                PublishType.project_id == project_id
            ).order_by(PublishType.code).all()

hierarchy_service = HierarchyService()