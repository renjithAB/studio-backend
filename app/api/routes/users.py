import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.auth.dependencies import get_current_user, get_db
from app.models.users import User
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.users import (
    UserListItem,
    UserCreate,
    UserUpdate,
    UserResponse,
    RoleResponse,
    RoleCreate,
    RoleUpdate,
    PermissionResponse
)

router = APIRouter()

SYSTEM_ROLES = {'production', 'junior', 'artist', 'senior', 'teams_lead', 'supervisor', 'internship', 'head'}


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def validate_id(id_value: int) -> int:
    if not isinstance(id_value, int):
        try:
            id_value = int(id_value)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="ID must be an integer")
    if id_value < 1000:
        raise HTTPException(status_code=400, detail="ID must be 1000 or greater")
    return id_value


# ── USERS CRUD ──────────────────────────────────────────────

@router.get("/list", response_model=List[UserListItem])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a lightweight list of all active users for dropdowns."""
    return db.query(User).filter(
        User.is_active == True,
        User.is_deleted == False,
    ).order_by(User.first_name, User.last_name).all()


@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all users with their associated role details."""
    return db.query(User).filter(
        User.is_deleted == False
    ).order_by(User.created_at.desc()).all()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new user with bcrypt-hashed password and role selection."""
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="A user with this email address already exists")

    if user_in.role_id:
        role_id = validate_id(user_in.role_id)
        if not db.query(Role).filter(Role.id == role_id, Role.is_active == True).first():
            raise HTTPException(status_code=404, detail="Role not found")

    new_user = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=user_in.is_active,
        private_key=hash_password(user_in.password),
        role_id=user_in.role_id,
        is_super=user_in.is_super,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user information, password, and role."""
    user_id = validate_id(user_id)
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email is not None and user_in.email != user.email:
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_in.email

    if user_in.first_name is not None:
        user.first_name = user_in.first_name
    if user_in.last_name is not None:
        user.last_name = user_in.last_name
    if user_in.password and user_in.password.strip():
        user.private_key = hash_password(user_in.password)
    if user_in.role_id is not None:
        if user_in.role_id == 0:
            user.role_id = None
        else:
            role_id = validate_id(user_in.role_id)
            if not db.query(Role).filter(Role.id == role_id, Role.is_active == True).first():
                raise HTTPException(status_code=404, detail="Role not found")
            user.role_id = role_id
    if user_in.is_super is not None:
        user.is_super = user_in.is_super
    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    user.updated_by = current_user.id
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a user."""
    user_id = validate_id(user_id)
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    user.is_deleted = True
    user.is_active = False
    user.updated_by = current_user.id
    db.commit()
    return {"message": "User deleted successfully", "id": user_id}


# ── ROLES CRUD ──────────────────────────────────────────────

@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all roles with their associated permissions."""
    return db.query(Role).filter(Role.is_active == True).order_by(Role.name).all()


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a custom role and associate selected permissions."""
    if db.query(Role).filter(Role.code == role_in.code).first():
        raise HTTPException(status_code=400, detail="A role with this code already exists")

    permissions = []
    if role_in.permission_ids:
        perm_ids = [validate_id(pid) for pid in role_in.permission_ids]
        permissions = db.query(Permission).filter(
            Permission.id.in_(perm_ids),
            Permission.is_active == True
        ).all()
        if len(permissions) != len(perm_ids):
            raise HTTPException(status_code=400, detail="One or more selected permissions are invalid")

    new_role = Role(
        code=role_in.code,
        name=role_in.name,
        description=role_in.description,
        is_active=True,
        created_by=current_user.id,
        updated_by=current_user.id,
        permissions=permissions
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a role's name, description, and permissions."""
    role_id = validate_id(role_id)
    role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role_in.name is not None:
        role.name = role_in.name
    if role_in.description is not None:
        role.description = role_in.description

    if role_in.permission_ids is not None:
        perm_ids = [validate_id(pid) for pid in role_in.permission_ids]
        permissions = db.query(Permission).filter(
            Permission.id.in_(perm_ids),
            Permission.is_active == True
        ).all()
        if len(permissions) != len(perm_ids):
            raise HTTPException(status_code=400, detail="One or more selected permissions are invalid")
        role.permissions = permissions

    role.updated_by = current_user.id
    db.commit()
    db.refresh(role)
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a custom role (system default roles are protected)."""
    role_id = validate_id(role_id)
    role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.code in SYSTEM_ROLES:
        raise HTTPException(status_code=400, detail="System default roles cannot be deleted")

    role.is_active = False
    role.updated_by = current_user.id
    db.commit()
    return {"message": "Role deleted successfully", "id": role_id}


# ── PERMISSIONS LIST ────────────────────────────────────────

@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all available permissions for role mapping."""
    return db.query(Permission).filter(
        Permission.is_active == True
    ).order_by(Permission.name).all()
