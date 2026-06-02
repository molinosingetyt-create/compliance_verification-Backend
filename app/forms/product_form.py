from typing import Optional

from pydantic import BaseModel


class CreateProductForm(BaseModel):
    name: str
    alias: str
    url: Optional[str] = None


class UpdateProductForm(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    url: Optional[str] = None
