from typing import Optional

from pydantic import BaseModel


class CreatePackagingAreaForm(BaseModel):
    name: str
    alias: str


class UpdatePackagingAreaForm(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
