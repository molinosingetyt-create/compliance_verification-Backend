from fastapi import APIRouter, Query
from app.controllers.grammage_controller import GrammageController
from app.forms.grammage_form import CreateGrammageForm
from app.schemas.response_schemas import (
    GrammageResponse,
    GrammageListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.get(
    "/list/all",
    tags=["grammage"],
    response_model=GrammageListResponse,
    responses={
        200: {
            "description": "Gramajes obtenidos exitosamente",
            "model": GrammageListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_grammages():
    """
    Obtiene todos los gramajes.

    **Respuestas:**
    - **200**: Retorna lista de gramajes exitosamente
    - **500**: Error al consultar la base de datos
    """
    return GrammageController.get_all()


@router.get(
    "/list",
    tags=["grammage"],
    response_model=GrammageResponse,
    responses={
        200: {
            "description": "Gramaje obtenido exitosamente",
            "model": GrammageResponse,
        },
        404: {
            "description": "Gramaje no encontrado",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_grammage_by_id(id: int = Query(..., description="ID del gramaje")):
    """
    Obtiene un gramaje por su ID.

    **Parámetros:**
    - **id**: ID único del gramaje

    **Respuestas:**
    - **200**: Gramaje encontrado y retornado exitosamente
    - **404**: No existe un gramaje con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return GrammageController.get_by_id(id)


@router.post(
    "/create",
    tags=["grammage"],
    response_model=GrammageResponse,
    responses={
        200: {
            "description": "Gramaje creado exitosamente",
            "model": GrammageResponse,
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
async def create_grammage(grammage_data: CreateGrammageForm):
    """
    Crea un nuevo gramaje.

    **Request Body:**
    - **name** (str): Nombre del gramaje
    - **alias** (str): Alias del gramaje
    - **tolerance** (str): tolerancia del gramaje

    **Respuestas:**
    - **200**: Gramaje creado exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear el gramaje en la base de datos
    """
    controller = GrammageController()
    return controller.create_grammage(grammage_data)
