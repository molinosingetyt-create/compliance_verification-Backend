from fastapi.middleware.cors import CORSMiddleware
from app.lib.config.config import settings


def configure_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,  # Permite todas las orígenes
        allow_credentials=True,
        allow_methods=["*"],  # Permite todos los métodos
        allow_headers=["*"],  # Permite todos los encabezados
    )
