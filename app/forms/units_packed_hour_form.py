from pydantic import BaseModel


class CreateUnitPackedHourForm(BaseModel):
    packaging_machine_id: int
    grammage_id: int
    value: str
