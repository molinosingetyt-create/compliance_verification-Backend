from pydantic import BaseModel


class CreateItemComplianceVerificationForm(BaseModel):
    nominal_quantity: str
    sample_weight_agm: str
    average_weight: str
    actual_quantity: str


class CreateComplianceVerificationForm(BaseModel):
    sampled: str
    product_id: int | None = None
    brand_id: int | None = None
    grammage_id: int | None = None
    analyzed: str
    machine_id: int | None = None
    lot_expires: str
    items: list[CreateItemComplianceVerificationForm]
