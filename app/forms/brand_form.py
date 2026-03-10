from pydantic import BaseModel


class CreateBrandForm(BaseModel):
    name: str
    alias: str
