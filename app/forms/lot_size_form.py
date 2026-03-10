from pydantic import BaseModel


class CreateLotSizeForm(BaseModel):
    name: str
    sample_size: str
    allowed_with_error: str
