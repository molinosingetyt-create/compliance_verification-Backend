from pydantic import BaseModel


class CreateGrammageForm(BaseModel):
    name: str
    alias: str
    tolerance: str
