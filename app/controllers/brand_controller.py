from typing import Optional

from fastapi import HTTPException

from app.lib.config.database import SessionLocal
from app.models.compliance_verification import ComplianceVerification
from app.models.parameters.brand import Brand


class BrandController:
    @staticmethod
    def _to_dict(row: Brand) -> dict:
        return row.toDict()

    @staticmethod
    def list_active():
        with SessionLocal() as db:
            rows = (
                db.query(Brand).filter(Brand.status == 1).order_by(Brand.id.asc()).all()
            )
            return {"data": [BrandController._to_dict(r) for r in rows]}

    @staticmethod
    def list_all():
        with SessionLocal() as db:
            rows = db.query(Brand).order_by(Brand.id.asc()).all()
            return [BrandController._to_dict(r) for r in rows]

    @staticmethod
    def get_by_id(brand_id: int, include_inactive: bool = False):
        with SessionLocal() as db:
            q = db.query(Brand).filter(Brand.id == brand_id)
            if not include_inactive:
                q = q.filter(Brand.status == 1)
            row = q.first()
            if not row:
                raise HTTPException(status_code=404, detail="Marca no encontrada")
            return BrandController._to_dict(row)

    @staticmethod
    def create(name: str, alias: str, url: Optional[str] = None):
        name = (name or "").strip()
        alias = (alias or "").strip()
        if not name or not alias:
            raise HTTPException(status_code=400, detail="Nombre y alias son obligatorios")
        with SessionLocal() as db:
            if db.query(Brand).filter(Brand.name == name).first():
                raise HTTPException(status_code=400, detail="Ya existe una marca con ese nombre")
            row = Brand(name=name, alias=alias, url=url, status=1)
            db.add(row)
            db.commit()
            db.refresh(row)
            return BrandController._to_dict(row)

    @staticmethod
    def update(
        brand_id: int,
        name: Optional[str] = None,
        alias: Optional[str] = None,
        url: Optional[str] = None,
        status: Optional[int] = None,
    ):
        with SessionLocal() as db:
            row = db.query(Brand).filter(Brand.id == brand_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Marca no encontrada")
            if name is not None:
                name = name.strip()
                if not name:
                    raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
                other = db.query(Brand).filter(Brand.name == name, Brand.id != row.id).first()
                if other:
                    raise HTTPException(status_code=400, detail="Ya existe una marca con ese nombre")
                row.name = name
            if alias is not None:
                row.alias = alias.strip()
            if url is not None:
                row.url = url.strip() or None
            if status is not None:
                row.status = status
            db.commit()
            db.refresh(row)
            return BrandController._to_dict(row)

    @staticmethod
    def delete(brand_id: int):
        with SessionLocal() as db:
            row = db.query(Brand).filter(Brand.id == brand_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Marca no encontrada")
            in_use = (
                db.query(ComplianceVerification)
                .filter(ComplianceVerification.brand_id == brand_id)
                .filter(ComplianceVerification.deleted_at.is_(None))
                .count()
            )
            if in_use > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede eliminar: usada en {in_use} verificación(es)",
                )
            row.status = 0
            db.commit()
            return {"detail": "Marca eliminada"}
