from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator
from app.controllers.compliance_verification_controller import (
    ComplianceVerificationController,
)
from app.forms.compliance_verification_form import CreateComplianceVerificationForm
from app.lib.config.database import get_db
from app.lib.security.deps import get_current_user, require_permission
from app.lib.security.rbac import get_user_permission_codes
from app.schemas.response_schemas import (
    ComplianceVerificationResponse,
    BadRequestResponse,
    FinalResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()

_COMPLIANCE_READ_CODES = frozenset({"sampling:view", "sampling:view-limited"})


def _require_compliance_read(user=Depends(get_current_user), db=Depends(get_db)):
    codes = get_user_permission_codes(db, user.id)
    if not codes & _COMPLIANCE_READ_CODES:
        raise HTTPException(status_code=403, detail="Sin permiso")
    return {"user": user, "codes": codes}


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
    user=Depends(require_permission("sampling:create")),
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
    return controller.create(compliance_verification_data, sampled_by_user_id=user.id)


@router.get("/list-all", tags=["compliance_verifications"])
async def list_compliance_verifications(
    ctx=Depends(_require_compliance_read),
    date_from: str | None = Query(None, alias="date_from"),
    date_to: str | None = Query(None, alias="date_to"),
):
    """
    **Respuestas:**
    - **200**: Lista de verificaciones de cumplimiento
    - **400**: Parámetros de consulta inválidos
    - **500**: Error al obtener las verificaciones de cumplimiento desde la base de datos
    """
    controller = ComplianceVerificationController()
    return controller.get_all(
        ctx["user"], ctx["codes"], date_from=date_from, date_to=date_to
    )


@router.get("/list/{id}", tags=["compliance_verifications"])
async def list_compliance_verifications_id(id: int, ctx=Depends(_require_compliance_read)):
    """

    Query Parameters:
    - **id** (int): ID de la verificación de cumplimiento a obtener.

        **Respuestas:**
        - **200**: Verificación de cumplimiento obtenida exitosamente
        - **400**: Parámetros de consulta inválidos
        - **500**: Error al obtener las verificaciones de cumplimiento desde la base de datos
    """
    controller = ComplianceVerificationController()
    return controller.get_by_id(id, ctx["user"], ctx["codes"])


@router.delete("/list/{id}", tags=["compliance_verifications"])
async def delete_compliance_verification(
    id: int,
    user=Depends(require_permission("sampling:delete")),
    db=Depends(get_db),
):
    """Elimina (oculta) un muestreo del listado y del dashboard."""
    codes = get_user_permission_codes(db, user.id)
    controller = ComplianceVerificationController()
    return controller.soft_delete(id, user, codes)


@router.get(
    "/list/{id}/package-weights",
    tags=["compliance_verifications"],
)
async def list_compliance_verification_package_weights(
    id: int, ctx=Depends(_require_compliance_read)
):
    """
    Devuelve los pesos de empaques (sin contenido) asociados a una verificación,
    y el promedio calculado.
    """
    controller = ComplianceVerificationController()
    return controller.get_package_weights(id, ctx["user"], ctx["codes"])


class UpdatePackageWeightsRequest(BaseModel):
    package_weights: list[float]


@router.put(
    "/list/{id}/package-weights",
    tags=["compliance_verifications"],
)
async def update_compliance_verification_package_weights(
    id: int,
    data: UpdatePackageWeightsRequest,
    user=Depends(require_permission("sampling:edit-package")),
    db=Depends(get_db),
):
    """Actualiza pesos de bolsas vacías y recalcula Qi, T1/T2 y veredicto del muestreo."""
    codes = get_user_permission_codes(db, user.id)
    controller = ComplianceVerificationController()
    return controller.update_package_weights(id, data.package_weights, user, codes)


class UpdateItemRequest(BaseModel):
    sample_weight_agm: Optional[float] = None
    actual_quantity: Optional[float] = None

    @model_validator(mode="after")
    def require_one_field(self):
        if self.sample_weight_agm is None and self.actual_quantity is None:
            raise ValueError("Debe enviar sample_weight_agm o actual_quantity")
        return self


@router.put(
    "/items/{item_id}",
    tags=["compliance_verifications"],
)
async def update_item_sampling(
    item_id: int,
    data: UpdateItemRequest,
    user=Depends(require_permission("sampling:edit")),
    db=Depends(get_db),
):
    """
    Edita un ítem del muestreo y recalcula la fila y el veredicto global.

    - **sample_weight_agm**: recalcula Qi (= AGM − promedio empaque), ATM y T1/T2.
    - **actual_quantity** (Qi): ajusta AGM coherente y recalcula T1/T2.

    Tras guardar reevalúa: errores T1/T2 por ítem, límite de T1 del lote,
    promedio neto vs nominal → status CUMPLE (1) / NO CUMPLE (2).
    """
    codes = get_user_permission_codes(db, user.id)
    controller = ComplianceVerificationController()
    return controller.update_item(
        item_id,
        sample_weight_agm=data.sample_weight_agm,
        actual_quantity=data.actual_quantity,
        user=user,
        permission_codes=codes,
    )
