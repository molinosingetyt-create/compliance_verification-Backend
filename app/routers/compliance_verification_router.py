from fastapi import APIRouter, Depends, Query
from app.controllers.compliance_verification_controller import (
    ComplianceVerificationController,
)
from app.forms.compliance_verification_form import CreateComplianceVerificationForm
from app.lib.config.database import get_db
from app.schemas.response_schemas import (
    ComplianceVerificationResponse,
    BadRequestResponse,
    FinalResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.post(
    "/create",
    tags=["compliance_verifications"],
    response_model=FinalResponse,
    responses={
        200: {
            "description": "Marca creada exitosamente",
            "model": FinalResponse,
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
async def create_compliance_verification(
    compliance_verification_data: CreateComplianceVerificationForm,
):
    """
        Crea una nueva verificación de cumplimiento junto con los items de muestreo.

    Request Body:
    - **sampled** (str): Persona que realiza el muestreo.
    - **product_id** (int | None): ID del producto asociado.
    - **brand_id** (int | None): ID de la marca del producto.
    - **grammage_id** (int | None): ID del gramaje del producto.
    - **analyzed** (str): Persona responsable del análisis.
    - **machine_id** (int | None): ID de la máquina utilizada.
    - **lot_expires** (str): Lote o fecha de vencimiento del producto.
    - **items** (list): Lista de registros de muestreo.

    Items (CreateItemComplianceVerificationForm):
    Cada elemento dentro de **items** contiene:

    - **sample_weight_agm** (str): Peso de la muestra AGM.
    - **average_weight** (str): Peso promedio calculado.

        **Respuestas:**
        - **200**: Verificación de cumplimiento creada exitosamente
        - **400**: Datos inválidos o campos requeridos faltantes
        - **500**: Error al crear la verificación de cumplimiento en la base de datos
    """
    controller = ComplianceVerificationController()
    return controller.create(compliance_verification_data)


@router.get("/list-all", tags=["compliance_verifications"])
async def list_compliance_verifications():
    """
    **Respuestas:**
    - **200**: Lista de verificaciones de cumplimiento
    - **400**: Parámetros de consulta inválidos
    - **500**: Error al obtener las verificaciones de cumplimiento desde la base de datos
    """
    controller = ComplianceVerificationController()
    return controller.get_all()


@router.get("/list/{id}", tags=["compliance_verifications"])
async def list_compliance_verifications_id(id: int):
    """

    Query Parameters:
    - **id** (int): ID de la verificación de cumplimiento a obtener.

        **Respuestas:**
        - **200**: Verificación de cumplimiento obtenida exitosamente
        - **400**: Parámetros de consulta inválidos
        - **500**: Error al obtener las verificaciones de cumplimiento desde la base de datos
    """
    controller = ComplianceVerificationController()
    return controller.get_by_id(id)
