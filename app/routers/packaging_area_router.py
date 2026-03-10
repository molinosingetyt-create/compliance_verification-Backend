from fastapi import APIRouter, Query
from app.controllers.packaging_area_controller import PackagingAreaController
from app.forms.packaking_area_form import CreatePackagingAreaForm
from app.schemas.response_schemas import (
    PackagingAreaResponse,
    PackagingAreaListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


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
async def get_all_packaging_areas():
    """
    Obtiene todas las áreas de empaque.

    **Respuestas:**
    - **200**: Retorna lista de áreas de empaque exitosamente
    - **500**: Error al consultar la base de datos
    """
    return PackagingAreaController.get_all()


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
    id: int = Query(..., description="ID del área de empaque")
):
    """
    Obtiene un área de empaque por su ID.

    **Parámetros:**
    - **id**: ID único del área de empaque

    **Respuestas:**
    - **200**: Área de empaque encontrada y retornado exitosamente
    - **404**: No existe un área de empaque con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return PackagingAreaController.get_by_id(id)


@router.post(
    "/create",
    tags=["packaging_areas"],
    response_model=PackagingAreaResponse,
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
    """
    Crea una nueva área de empaque.

    **Request Body:**
    - **name** (str): Nombre del área de empaque
    - **alias** (str): Alias del producto

    **Respuestas:**
    - **200**: Producto creado exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear el área de empaque en la base de datos
    """
    controller = PackagingAreaController()
    return controller.create_packaging_area(packaging_area_data)
