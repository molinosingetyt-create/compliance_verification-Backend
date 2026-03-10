from pydantic import BaseModel


class CreatePackagingMachineForm(BaseModel):
    name: str
    alias: str
    packaging_area_id: int
