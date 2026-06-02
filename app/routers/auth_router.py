from fastapi import APIRouter
from pydantic import BaseModel

from app.controllers.auth_controller import AuthController


router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", tags=["auth"])
async def login(data: LoginRequest):
    return AuthController.login(data.username, data.password)

