from pydantic import BaseModel


class CreatePackagingAreaForm(BaseModel):
    name: str
    alias: str
