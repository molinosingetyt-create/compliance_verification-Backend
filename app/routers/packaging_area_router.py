from fastapi import APIRouter, Depends, Query

from app.controllers.packaging_area_controller import PackagingAreaController
from app.forms.packaking_area_form import CreatePackagingAreaForm, UpdatePackagingAreaForm
from app.lib.security.deps import get_current_user, require_permission
from app.schemas.response_schemas import (
    PackagingAreaResponse,
    PackagingAreaListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()
_manage = Depends(require_permission("catalog:manage"))


@router.get(
    "/list/all",
    tags=["packaging_areas"],
    response_model=PackagingAreaListResponse,
    responses={
        200: {
            "description": "Áreas de empaque obtenidas exitosamente",
            "model": PackagingAreaListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_packaging_areas(_user=Depends(get_current_user)):
    """Listado activo para selects y dashboard."""
    return PackagingAreaController.list_active()


@router.get("/manage", tags=["packaging_areas"], dependencies=[_manage])
async def manage_list_packaging_areas():
    return PackagingAreaController.list_all()


@router.get(
    "/list",
    tags=["packaging_areas"],
    response_model=PackagingAreaResponse,
    responses={
        200: {
            "description": "Área de empaque obtenida exitosamente",
            "model": PackagingAreaResponse,
        },
        404: {
            "description": "Área de empaque no encontrada",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_packaging_area_by_id(
    id: int = Query(..., description="ID del área de empaque"),
    _user=Depends(get_current_user),
):
    return PackagingAreaController.get_by_id(id)


@router.get("/{packaging_area_id}", tags=["packaging_areas"], dependencies=[_manage])
async def get_packaging_area_by_path_id(packaging_area_id: int):
    return PackagingAreaController.get_by_id(packaging_area_id, include_inactive=True)


@router.post(
    "/create",
    tags=["packaging_areas"],
    response_model=PackagingAreaResponse,
    dependencies=[_manage],
    responses={
        200: {
            "description": "Área de empaque creada exitosamente",
            "model": PackagingAreaResponse,
        },
        400: {
            "description": "Solicitud inválida - Campos requeridos faltantes",
            "model": BadRequestResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def create_packaging_area(packaging_area_data: CreatePackagingAreaForm):
    return PackagingAreaController.create(packaging_area_data.name, packaging_area_data.alias)


@router.put("/{packaging_area_id}", tags=["packaging_areas"], dependencies=[_manage])
async def update_packaging_area(packaging_area_id: int, body: UpdatePackagingAreaForm):
    return PackagingAreaController.update(packaging_area_id, body.name, body.alias)


@router.delete("/{packaging_area_id}", tags=["packaging_areas"], dependencies=[_manage])
async def delete_packaging_area(packaging_area_id: int):
    return PackagingAreaController.delete(packaging_area_id)
