"""
Esquemas de respuesta para documentación en Swagger/OpenAPI
"""

from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, List, Any


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Descripción del error"}}
    )


class SuccessResponse(BaseModel):
    """Modelo genérico para respuestas exitosas"""

    data: Any
    message: str = "Operación exitosa"

    model_config = ConfigDict(
        json_schema_extra={"example": {"data": {}, "message": "Operación exitosa"}}
    )


class ProductResponse(BaseModel):
    """Modelo de respuesta para un producto"""

    id: int
    name: str
    alias: str
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "name": "Producto XXX", "alias": "PXXX", "status": 1}
        }
    )


class BrandResponse(BaseModel):
    """Modelo de respuesta para una marca"""

    id: int
    name: str
    alias: str
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "name": "Marca XXX", "alias": "MXXX", "status": 1}
        }
    )
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "name": "Marca XXX", "alias": "MXXX", "status": 1}
        }
    )


class ProductListResponse(BaseModel):
    """Modelo de respuesta para lista de productos"""

    data: List[ProductResponse]
    message: str = "Productos obtenidos exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {"id": 1, "name": "Producto 1", "alias": "P1", "status": 1},
                    {"id": 2, "name": "Producto 2", "alias": "P2", "status": 1},
                ],
                "message": "Productos obtenidos exitosamente",
            }
        }
    )


class BrandListResponse(BaseModel):
    """Modelo de respuesta para lista de marcas"""

    data: List[BrandResponse]
    message: str = "Marcas obtenidas exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {"id": 1, "name": "Marca 1", "alias": "M1", "status": 1},
                    {"id": 2, "name": "Marca 2", "alias": "M2", "status": 1},
                ],
                "message": "Marcas obtenidas exitosamente",
            }
        }
    )


class BadRequestResponse(BaseModel):
    """Modelo para errores de validación (400)"""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "Solicitud inválida - Campos requeridos faltantes"}
        }
    )


class NotFoundResponse(BaseModel):
    """Modelo para recurso no encontrado (404)"""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Producto no encontrado"}}
    )


class InternalServerErrorResponse(BaseModel):
    """Modelo para errores internos del servidor (500)"""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "Error al obtener datos: [descripción del error]"}
        }
    )


class PackagingAreaResponse(BaseModel):
    """Modelo de respuesta para un área de empaque"""

    id: int
    name: str
    alias: str
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Área de Empaque 1",
                "alias": "AE1",
                "status": 1,
            }
        }
    )


class PackagingAreaListResponse(BaseModel):
    """Modelo de respuesta para lista de áreas de empaque"""

    data: List[PackagingAreaResponse]
    message: str = "Áreas de empaque obtenidas exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {"id": 1, "name": "Área de Empaque 1", "alias": "AE1", "status": 1},
                    {"id": 2, "name": "Área de Empaque 2", "alias": "AE2", "status": 1},
                ],
                "message": "Áreas de empaque obtenidas exitosamente",
            }
        }
    )


class PackagingMachineResponse(BaseModel):
    """Modelo de respuesta para una máquina de empaque"""

    id: int
    name: str
    alias: str
    packaging_area_id: int
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Máquina de Empaque 1",
                "alias": "ME1",
                "packaging_area_id": 1,
                "status": 1,
            }
        }
    )


class PackagingMachineListResponse(BaseModel):
    """Modelo de respuesta para lista de máquinas de empaque"""

    data: List[PackagingMachineResponse]
    message: str = "Máquinas de empaque obtenidas exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "name": "Máquina de Empaque 1",
                        "alias": "ME1",
                        "packaging_area_id": 1,
                        "status": 1,
                    },
                    {
                        "id": 2,
                        "name": "Máquina de Empaque 2",
                        "alias": "ME2",
                        "packaging_area_id": 1,
                        "status": 1,
                    },
                ],
                "message": "Máquinas de empaque obtenidas exitosamente",
            }
        }
    )


class GrammageResponse(BaseModel):
    """Modelo de respuesta para un gramaje"""

    id: int
    name: str
    alias: str
    tolerance: str
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Gramaje 1",
                "alias": "G1",
                "tolerance": "±5%",
                "packaging_area_id": 1,
                "status": 1,
            }
        }
    )


class GrammageListResponse(BaseModel):
    """Modelo de respuesta para lista de gramajes"""

    data: List[GrammageResponse]
    message: str = "Gramajes obtenidos exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "name": "Gramaje 1",
                        "alias": "G1",
                        "tolerance": "±5%",
                        "packaging_area_id": 1,
                        "status": 1,
                    },
                    {
                        "id": 2,
                        "name": "Gramaje 2",
                        "alias": "G2",
                        "tolerance": "±10%",
                        "packaging_area_id": 1,
                        "status": 1,
                    },
                ],
                "message": "Gramajes obtenidos exitosamente",
            }
        }
    )


class UnitsPackedHourResponse(BaseModel):
    """Modelo de respuesta para una unidad empaquetada por hora"""

    id: int
    packaging_machine_id: int
    grammage_id: int
    value: str
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "packaging_machine_id": 1,
                "grammage_id": 1,
                "value": "100 unidades/hora",
                "status": 1,
            }
        }
    )


class UnitsPackedHourListResponse(BaseModel):
    """Modelo de respuesta para lista de unidades empaquetadas por hora"""

    data: List[UnitsPackedHourResponse]
    message: str = "Unidades empaquetadas por hora obtenidas exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "packaging_machine_id": 1,
                        "grammage_id": 1,
                        "value": "100 unidades/hora",
                        "status": 1,
                    },
                    {
                        "id": 2,
                        "packaging_machine_id": 1,
                        "grammage_id": 2,
                        "value": "150 unidades/hora",
                        "status": 1,
                    },
                ],
                "message": "Unidades empaquetadas por hora obtenidas exitosamente",
            }
        }
    )


class LotSizeResponse(BaseModel):
    """Modelo de respuesta para un tamaño de lote"""

    id: int
    name: str
    sample_size: str
    allowed_with_error: str
    status: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Tamaño de Lote 1",
                "sample_size": "50 unidades",
                "allowed_with_error": "±5 unidades",
                "status": 1,
            }
        }
    )


class LotSizeListResponse(BaseModel):
    """Modelo de respuesta para lista de tamaños de lote"""

    data: List[LotSizeResponse]
    message: str = "Tamaños de lote obtenidos exitosamente"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "name": "Tamaño de Lote 1",
                        "sample_size": "50 unidades",
                        "allowed_with_error": "±5 unidades",
                        "status": 1,
                    },
                    {
                        "id": 2,
                        "name": "Tamaño de Lote 2",
                        "sample_size": "100 unidades",
                        "allowed_with_error": "±10 unidades",
                        "status": 1,
                    },
                ],
                "message": "Tamaños de lote obtenidos exitosamente",
            }
        }
    )


class ItemComplianceVerificationResponse(BaseModel):
    id: int
    compliance_verification_id: int
    nominal_quantity: str  # Coincide con tu Column(String)
    sample_weight_agm: str
    average_weight: str
    actual_quantity: str
    status: int

    model_config = ConfigDict(from_attributes=True)


class ComplianceVerificationResponse(BaseModel):
    id: int
    sampled: str
    product_id: Optional[int]
    brand_id: Optional[int]
    grammage_id: Optional[int]
    analyzed: str
    machine_id: Optional[int]
    lot_expires: str
    status: int
    # Importante: El nombre debe ser igual al backref en el modelo ItemComplianceVerification
    item_compliance_verifications: List[ItemComplianceVerificationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class FinalResponse(BaseModel):
    detail: str  # Usamos detail para que Angular lo lea directo en la modal
    result: int
    errors_found: Dict[str, int]
    allowed_t1: int
    data: Any  # Any evita que el ResponseValidationError truene si hay nulos

    model_config = ConfigDict(from_attributes=True)
