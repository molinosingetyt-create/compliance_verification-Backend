from typing import Optional

from pydantic import BaseModel


class CreateGrammageForm(BaseModel):
    name: str
    alias: str
    tolerance: str
    url: Optional[str] = None


class UpdateGrammageForm(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    tolerance: Optional[str] = None
    url: Optional[str] = None
