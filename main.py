from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.lib.config.middleware import configure_cors
from app.routers import (
    product_router,
    brand_router,
    packaging_area_router,
    packaging_machine_router,
    grammage_router,
    units_packed_hour_router,
    lot_size_router,
)
from app.lib.config.database import engine
from app.models import Base

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crea las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Compliance Verification API",
    description="API para gestión de productos y cumplimiento",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

configure_cors(app)
file_dir = os.path.join(os.getcwd(), "file")
tmp_dir = os.path.join(os.getcwd(), "tmp")
if os.path.exists(file_dir):
    app.mount("/file", StaticFiles(directory=file_dir), name="file")
    app.mount("/tmp", StaticFiles(directory=tmp_dir), name="tmp")


app.include_router(product_router.router, prefix="/v1/products")
app.include_router(brand_router.router, prefix="/v1/brands")
app.include_router(packaging_area_router.router, prefix="/v1/packaging_areas")
app.include_router(packaging_machine_router.router, prefix="/v1/packaging_machines")
app.include_router(grammage_router.router, prefix="/v1/grammage")
app.include_router(units_packed_hour_router.router, prefix="/v1/units_packed_hour")
app.include_router(lot_size_router.router, prefix="/v1/lot_sizes")
