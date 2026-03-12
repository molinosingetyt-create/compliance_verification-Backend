from pydantic import BaseModel


class CreateItemComplianceVerificationForm(BaseModel):
    sample_weight_agm: str
    average_weight: str


class CreateComplianceVerificationForm(BaseModel):
    sampled: str
    product_id: int | None = None
    brand_id: int | None = None
    grammage_id: int | None = None
    analyzed: str
    machine_id: int | None = None
    lot_expires: str
    items: list[CreateItemComplianceVerificationForm]
