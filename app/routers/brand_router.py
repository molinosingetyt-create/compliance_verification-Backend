from fastapi import APIRouter, Depends, Query
from app.controllers.brand_controller import BrandController
from app.forms.brand_form import CreateBrandForm
from app.lib.config.database import get_db
from app.schemas.response_schemas import (
    BrandListResponse,
    BrandResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.get(
    "/list/all",
    tags=["brands"],
    response_model=BrandListResponse,
    responses={
        200: {
            "description": "Marcas obtenidas exitosamente",
            "model": BrandListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_brands():
    """
    Obtiene todas las marcas.

    **Respuestas:**
    - **200**: Retorna lista de marcas exitosamente
    - **500**: Error al consultar la base de datos
    """
    return BrandController.get_all()


@router.get(
    "/list",
    tags=["brands"],
    response_model=BrandResponse,
    responses={
        200: {
            "description": "Marca obtenida exitosamente",
            "model": BrandResponse,
        },
        404: {
            "description": "Marca no encontrada",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_brand_by_id(id: int = Query(..., description="ID de la marca")):
    """
    Obtiene una marca por su ID.

    **Parámetros:**
    - **id**: ID único de la marca

    **Respuestas:**
    - **200**: Marca encontrada y retornado exitosamente
    - **404**: No existe una marca con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return BrandController.get_by_id(id)


@router.post(
    "/create",
    tags=["brands"],
    response_model=BrandResponse,
    responses={
        200: {
            "description": "Marca creada exitosamente",
            "model": BrandResponse,
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
async def create_brand(brand_data: CreateBrandForm):
    """
    Crea una nueva marca.

    **Request Body:**
    - **name** (str): Nombre de la marca
    - **alias** (str): Alias de la marca

    **Respuestas:**
    - **200**: Marca creada exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear la marca en la base de datos
    """
    controller = BrandController()
    return controller.create_brand(brand_data)
