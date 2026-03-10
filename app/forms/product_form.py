from pydantic import BaseModel


class CreateProductForm(BaseModel):
    name: str
    alias: str
