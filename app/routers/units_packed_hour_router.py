from fastapi import APIRouter, Query
from app.controllers.units_packed_hour_controller import UnitsPackedHourController
from app.forms.units_packed_hour_form import CreateUnitPackedHourForm
from app.schemas.response_schemas import (
    UnitsPackedHourResponse,
    UnitsPackedHourListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.get(
    "/list/all",
    tags=["units_packed_hour"],
    response_model=UnitsPackedHourListResponse,
    responses={
        200: {
            "description": "Unidades empaquetadas por hora obtenidas exitosamente",
            "model": UnitsPackedHourListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_units_packed_hours():
    """
    Obtiene todas las unidades empaquetadas por hora.

    **Respuestas:**
    - **200**: Retorna lista de unidades empaquetadas por hora exitosamente
    - **500**: Error al consultar la base de datos
    """
    return UnitsPackedHourController.get_all()


@router.get(
    "/list",
    tags=["units_packed_hour"],
    response_model=UnitsPackedHourResponse,
    responses={
        200: {
            "description": "Unidad empaquetada por hora obtenida exitosamente",
            "model": UnitsPackedHourResponse,
        },
        404: {
            "description": "Unidad empaquetada por hora no encontrada",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_units_packed_hour_by_id(
    id: int = Query(..., description="ID de la unidad empaquetada por hora")
):
    """
    Obtiene una unidad empaquetada por hora por su ID.

    **Parámetros:**
    - **id**: ID único de la unidad empaquetada por hora

    **Respuestas:**
    - **200**: Unidad empaquetada por hora encontrada y retornado exitosamente
    - **404**: No existe una unidad empaquetada por hora con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return UnitsPackedHourController.get_by_id(id)


@router.post(
    "/create",
    tags=["units_packed_hour"],
    response_model=UnitsPackedHourResponse,
    responses={
        200: {
            "description": "Unidad empaquetada por hora creada exitosamente",
            "model": UnitsPackedHourResponse,
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
async def create_units_packed_hour(units_packed_hour_data: CreateUnitPackedHourForm):
    """
    Crea una nueva unidad empaquetada por hora.

    **Request Body:**
    - **packaging_machine_id** (int): ID de la máquina de empaque
    - **grammage_id** (int): ID del gramaje
    - **value** (str): Valor de la unidad empaquetada por hora

    **Respuestas:**
    - **200**: Unidad empaquetada por hora creada exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear la unidad empaquetada por hora en la base de datos
    """
    controller = UnitsPackedHourController()
    return controller.create_units_packed_hour(units_packed_hour_data)
