from typing import Optional

from fastapi import HTTPException
from app.lib.config.database import SessionLocal
from app.models.compliance_verification import ComplianceVerification
from app.models.parameters.product import Product


class ProductController:
    @staticmethod
    def _to_dict(row: Product) -> dict:
        return row.toDict()

    @staticmethod
    def list_active():
        with SessionLocal() as db:
            rows = (
                db.query(Product)
                .filter(Product.status == 1)
                .order_by(Product.id.asc())
                .all()
            )
            return {"data": [ProductController._to_dict(r) for r in rows]}

    @staticmethod
    def list_all():
        with SessionLocal() as db:
            rows = db.query(Product).order_by(Product.id.asc()).all()
            return [ProductController._to_dict(r) for r in rows]

    @staticmethod
    def get_by_id(product_id: int, include_inactive: bool = False):
        with SessionLocal() as db:
            q = db.query(Product).filter(Product.id == product_id)
            if not include_inactive:
                q = q.filter(Product.status == 1)
            row = q.first()
            if not row:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return ProductController._to_dict(row)

    @staticmethod
    def create(name: str, alias: str, url: Optional[str] = None):
        name = (name or "").strip()
        alias = (alias or "").strip()
        if not name or not alias:
            raise HTTPException(status_code=400, detail="Nombre y alias son obligatorios")
        with SessionLocal() as db:
            if db.query(Product).filter(Product.name == name).first():
                raise HTTPException(status_code=400, detail="Ya existe un producto con ese nombre")
            row = Product(name=name, alias=alias, url=url, status=1)
            db.add(row)
            db.commit()
            db.refresh(row)
            return ProductController._to_dict(row)

    @staticmethod
    def update(
        product_id: int,
        name: Optional[str] = None,
        alias: Optional[str] = None,
        url: Optional[str] = None,
        status: Optional[int] = None,
    ):
        with SessionLocal() as db:
            row = db.query(Product).filter(Product.id == product_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            if name is not None:
                name = name.strip()
                if not name:
                    raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
                other = db.query(Product).filter(Product.name == name, Product.id != row.id).first()
                if other:
                    raise HTTPException(status_code=400, detail="Ya existe un producto con ese nombre")
                row.name = name
            if alias is not None:
                row.alias = alias.strip()
            if url is not None:
                row.url = url.strip() or None
            if status is not None:
                row.status = status
            db.commit()
            db.refresh(row)
            return ProductController._to_dict(row)

    @staticmethod
    def delete(product_id: int):
        with SessionLocal() as db:
            row = db.query(Product).filter(Product.id == product_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            in_use = (
                db.query(ComplianceVerification)
                .filter(ComplianceVerification.product_id == product_id)
                .filter(ComplianceVerification.deleted_at.is_(None))
                .count()
            )
            if in_use > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede eliminar: usado en {in_use} verificación(es)",
                )
            row.status = 0
            db.commit()
            return {"detail": "Producto eliminado"}
