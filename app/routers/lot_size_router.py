from fastapi import APIRouter, Query
from app.controllers.lot_size_controller import LotSizeController
from app.forms.lot_size_form import CreateLotSizeForm
from app.schemas.response_schemas import (
    LotSizeResponse,
    LotSizeListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.get(
    "/list/all",
    tags=["lot_sizes"],
    response_model=LotSizeListResponse,
    responses={
        200: {
            "description": "Tamaños de lote obtenidos exitosamente",
            "model": LotSizeListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_lot_sizes():
    """
    Obtiene todos los tamaños de lote.

    **Respuestas:**
    - **200**: Retorna lista de tamaños de lote exitosamente
    - **500**: Error al consultar la base de datos
    """
    return LotSizeController.get_all()


@router.get(
    "/list",
    tags=["lot_sizes"],
    response_model=LotSizeResponse,
    responses={
        200: {
            "description": "Tamaño de lote obtenido exitosamente",
            "model": LotSizeResponse,
        },
        404: {
            "description": "Tamaño de lote no encontrado",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_lot_size_by_id(id: int = Query(..., description="ID del tamaño de lote")):
    """
    Obtiene un tamaño de lote por su ID.

    **Parámetros:**
    - **id**: ID único del tamaño de lote

    **Respuestas:**
    - **200**: Tamaño de lote encontrado y retornado exitosamente
    - **404**: No existe un tamaño de lote con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return LotSizeController.get_by_id(id)


@router.post(
    "/create",
    tags=["lot_sizes"],
    response_model=LotSizeResponse,
    responses={
        200: {
            "description": "Tamaño de lote creado exitosamente",
            "model": LotSizeResponse,
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
async def create_lot_size(lot_size_data: CreateLotSizeForm):
    """
    Crea un nuevo tamaño de lote.

    **Request Body:**
    - **name** (str): Nombre del tamaño de lote
    - **sample_size** (str): Tamaño de la muestra
    - **allowed_with_error** (str): Permitido con error

    **Respuestas:**
    - **200**: Tamaño de lote creado exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear el tamaño de lote en la base de datos
    """
    controller = LotSizeController()
    return controller.create_lot_size(lot_size_data)
