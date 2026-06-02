from pydantic import BaseModel
from typing import Union


class CreateItemComplianceVerificationForm(BaseModel):
    sample_weight_agm: str
    average_weight: str


class CreateComplianceVerificationForm(BaseModel):
    sampled: str
    market_destination: str
    product_id: int | None = None
    brand_id: int | None = None
    grammage_id: int | None = None
    analyzed: str
    machine_id: int | None = None
    lot_expires: str
    # Acepta pesos como número o string (viene del frontend como number).
    package_weights: list[Union[str, float, int]] = []
    items: list[CreateItemComplianceVerificationForm]
