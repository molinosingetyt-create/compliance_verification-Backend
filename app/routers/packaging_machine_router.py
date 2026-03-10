from fastapi import APIRouter, Query
from app.controllers.packaging_machine_controller import PackagingMachineController
from app.forms.packaking_machine_form import CreatePackagingMachineForm
from app.schemas.response_schemas import (
    PackagingMachineResponse,
    PackagingMachineListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.get(
    "/list/all",
    tags=["packaging_machines"],
    response_model=PackagingMachineListResponse,
    responses={
        200: {
            "description": "Máquinas de empaque obtenidas exitosamente",
            "model": PackagingMachineListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_packaging_machines():
    """
    Obtiene todas las máquinas de empaque.

    **Respuestas:**
    - **200**: Retorna lista de máquinas de empaque exitosamente
    - **500**: Error al consultar la base de datos
    """
    return PackagingMachineController.get_all()


@router.get(
    "/list",
    tags=["packaging_machines"],
    response_model=PackagingMachineResponse,
    responses={
        200: {
            "description": "Máquina de empaque obtenida exitosamente",
            "model": PackagingMachineResponse,
        },
        404: {
            "description": "Máquina de empaque no encontrada",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_packaging_machine_by_id(
    id: int = Query(..., description="ID de la máquina de empaque")
):
    """
    Obtiene una máquina de empaque por su ID.

    **Parámetros:**
    - **id**: ID único de la máquina de empaque

    **Respuestas:**
    - **200**: Máquina de empaque encontrada y retornado exitosamente
    - **404**: No existe una máquina de empaque con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return PackagingMachineController.get_by_id(id)


@router.post(
    "/create",
    tags=["packaging_machines"],
    response_model=PackagingMachineResponse,
    responses={
        200: {
            "description": "Máquina de empaque creada exitosamente",
            "model": PackagingMachineResponse,
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
async def create_packaging_machine(packaging_machine_data: CreatePackagingMachineForm):
    """
    Crea una nueva máquina de empaque.

    **Request Body:**
    - **name** (str): Nombre de la máquina de empaque
    - **alias** (str): Alias de la máquina de empaque
    - **packaging_area_id** (int): ID del área de empaque a la que pertenece la máquina

    **Respuestas:**
    - **200**: Máquina de empaque creada exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear la máquina de empaque en la base de datos
    """
    controller = PackagingMachineController()
    return controller.create_packaging_machine(packaging_machine_data)
