from typing import Optional

from pydantic import BaseModel


class CreateBrandForm(BaseModel):
    name: str
    alias: str
    url: Optional[str] = None


class UpdateBrandForm(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    url: Optional[str] = None
