from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.controllers.admin_controller import AdminController
from app.lib.security.deps import require_permission

router = APIRouter(dependencies=[Depends(require_permission("users:manage"))])


# ——— Permisos ———
class PermissionBody(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionUpdateBody(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None


@router.get("/permissions", tags=["admin"])
async def admin_list_permissions():
    return AdminController.list_permissions()


@router.get("/permissions/{permission_id}", tags=["admin"])
async def admin_get_permission(permission_id: int):
    return AdminController.get_permission(permission_id)


@router.post("/permissions", tags=["admin"])
async def admin_create_permission(body: PermissionBody):
    return AdminController.create_permission(body.code, body.description)


@router.put("/permissions/{permission_id}", tags=["admin"])
async def admin_update_permission(permission_id: int, body: PermissionUpdateBody):
    return AdminController.update_permission(permission_id, body.code, body.description)


@router.delete("/permissions/{permission_id}", tags=["admin"])
async def admin_delete_permission(permission_id: int):
    return AdminController.delete_permission(permission_id)


# ——— Perfiles ———
class RoleBody(BaseModel):
    name: str
    permission_ids: list[int] = Field(default_factory=list)


class RoleUpdateBody(BaseModel):
    name: Optional[str] = None
    permission_ids: Optional[list[int]] = None


class SetRolePermissionsBody(BaseModel):
    permission_ids: list[int] = Field(default_factory=list)


@router.get("/roles", tags=["admin"])
async def admin_list_roles():
    return AdminController.list_roles()


@router.get("/roles/{role_id}", tags=["admin"])
async def admin_get_role(role_id: int):
    return AdminController.get_role(role_id)


@router.post("/roles", tags=["admin"])
async def admin_create_role(body: RoleBody):
    return AdminController.create_role(body.name, body.permission_ids)


@router.put("/roles/{role_id}", tags=["admin"])
async def admin_update_role(role_id: int, body: RoleUpdateBody):
    return AdminController.update_role(role_id, body.name, body.permission_ids)


@router.delete("/roles/{role_id}", tags=["admin"])
async def admin_delete_role(role_id: int):
    return AdminController.delete_role(role_id)


@router.put("/roles/{role_id}/permissions", tags=["admin"])
async def admin_set_role_permissions(role_id: int, body: SetRolePermissionsBody):
    return AdminController.set_role_permissions(role_id, body.permission_ids)


# ——— Usuarios ———
class CreateUserBody(BaseModel):
    username: str
    password: str
    role_id: int
    is_active: bool = True
    full_name: Optional[str] = None


class UpdateUserBody(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None


@router.get("/users", tags=["admin"])
async def admin_list_users():
    return AdminController.list_users()


@router.get("/users/{user_id}", tags=["admin"])
async def admin_get_user(user_id: int):
    return AdminController.get_user(user_id)


@router.post("/users", tags=["admin"])
async def admin_create_user(body: CreateUserBody):
    return AdminController.create_user(
        body.username, body.password, body.role_id, body.is_active, body.full_name
    )


@router.put("/users/{user_id}", tags=["admin"])
async def admin_update_user(user_id: int, body: UpdateUserBody):
    return AdminController.update_user(
        user_id,
        body.username,
        body.password,
        body.role_id,
        body.is_active,
        body.full_name,
    )


@router.delete("/users/{user_id}", tags=["admin"])
async def admin_delete_user(user_id: int):
    return AdminController.delete_user(user_id)
