import os

os.environ.setdefault("TZ", "America/Bogota")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.lib.config.middleware import configure_cors
from app.lib.config.config import settings
from app.lib.config.database import SessionLocal
from app.routers import (
    admin_router,
    auth_router,
    product_router,
    brand_router,
    packaging_area_router,
    packaging_machine_router,
    grammage_router,
    units_packed_hour_router,
    lot_size_router,
    compliance_verification_router,
)
from app.lib.config.database import engine
from app.models import Base
from app.models.seeders_executed import run_seeder

from seeders.parameter_seeders import (
    seed_brands,
    seed_grammages,
    seed_lot_sizes,
    seed_packaging_areas,
    seed_packaging_machines,
    seed_products,
    seed_units_packed_hour,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_schema_columns():
    """Añade columnas nuevas en BD existentes (PostgreSQL)."""
    from sqlalchemy import text

    statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(150)",
        "ALTER TABLE compliance_verifications ADD COLUMN IF NOT EXISTS market_destination VARCHAR(30)",
        "ALTER TABLE compliance_verifications ADD COLUMN IF NOT EXISTS sampled_by_user_id INTEGER",
        "ALTER TABLE compliance_verifications ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS packaging_area_id INTEGER",
    ]
    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()


def run_all_seeders():
    db = SessionLocal()
    run_seeder(db, "seed_brands", seed_brands)
    run_seeder(db, "seed_grammages", seed_grammages)
    run_seeder(db, "seed_lot_sizes", seed_lot_sizes)
    run_seeder(db, "seed_packaging_areas", seed_packaging_areas)
    run_seeder(db, "seed_packaging_machines", seed_packaging_machines)
    run_seeder(db, "seed_products", seed_products)
    run_seeder(db, "seed_units_packed_hour", seed_units_packed_hour)
    db.close()


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
app.include_router(auth_router.router, prefix="/v1/auth")
app.include_router(admin_router.router, prefix="/v1/admin")
app.include_router(
    compliance_verification_router.router, prefix="/v1/compliance_verifications"
)

@app.on_event("startup")
def on_startup():
    # No hacemos fallar el servidor si la DB está caída/mal configurada.
    # En ese caso, los endpoints que requieran DB fallarán cuando intenten usarla,
    # pero el proceso se mantiene vivo y deja el error en logs.
    try:
        Base.metadata.create_all(bind=engine)
        ensure_schema_columns()
    except Exception:
        logger.exception("Error conectando/initializando la base de datos (create_all).")
        return

    try:
        run_all_seeders()
    except Exception:
        logger.exception("Error ejecutando seeders en startup.")

    # Crear/actualizar admin desde .env (vía pydantic settings, no os.getenv).
    try:
        from app.controllers.auth_controller import AuthController
        from app.controllers.rbac_controller import RbacController

        with SessionLocal() as db:
            RbacController.seed(db)
            AuthController.ensure_default_admin(
                db,
                settings.DEFAULT_ADMIN_USER,
                settings.DEFAULT_ADMIN_PASS,
            )
            if settings.DEFAULT_ADMIN_USER:
                logger.info(
                    "Auth: usuario administrador configurado (%s)",
                    settings.DEFAULT_ADMIN_USER,
                )
    except Exception:
        logger.exception("Error inicializando auth (roles/admin).")
