from typing import Optional

from fastapi import HTTPException

from app.lib.config.database import SessionLocal
from app.models.compliance_verification import ComplianceVerification
from app.models.parameters.grammage import Grammage


class GrammageController:
    @staticmethod
    def _to_dict(row: Grammage) -> dict:
        return row.toDict()

    @staticmethod
    def list_active():
        with SessionLocal() as db:
            rows = (
                db.query(Grammage)
                .filter(Grammage.status == 1)
                .order_by(Grammage.id.asc())
                .all()
            )
            return {"data": [GrammageController._to_dict(r) for r in rows]}

    @staticmethod
    def list_all():
        with SessionLocal() as db:
            rows = db.query(Grammage).order_by(Grammage.id.asc()).all()
            return [GrammageController._to_dict(r) for r in rows]

    @staticmethod
    def get_by_id(grammage_id: int, include_inactive: bool = False):
        with SessionLocal() as db:
            q = db.query(Grammage).filter(Grammage.id == grammage_id)
            if not include_inactive:
                q = q.filter(Grammage.status == 1)
            row = q.first()
            if not row:
                raise HTTPException(status_code=404, detail="Gramaje no encontrado")
            return GrammageController._to_dict(row)

    @staticmethod
    def create(name: str, alias: str, tolerance: str, url: Optional[str] = None):
        name = (name or "").strip()
        alias = (alias or "").strip()
        tolerance = (tolerance or "").strip()
        if not name or not alias or not tolerance:
            raise HTTPException(
                status_code=400, detail="Nombre, alias y tolerancia son obligatorios"
            )
        with SessionLocal() as db:
            if db.query(Grammage).filter(Grammage.name == name).first():
                raise HTTPException(status_code=400, detail="Ya existe un gramaje con ese nombre")
            row = Grammage(name=name, alias=alias, tolerance=tolerance, url=url, status=1)
            db.add(row)
            db.commit()
            db.refresh(row)
            return GrammageController._to_dict(row)

    @staticmethod
    def update(
        grammage_id: int,
        name: Optional[str] = None,
        alias: Optional[str] = None,
        tolerance: Optional[str] = None,
        url: Optional[str] = None,
        status: Optional[int] = None,
    ):
        with SessionLocal() as db:
            row = db.query(Grammage).filter(Grammage.id == grammage_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Gramaje no encontrado")
            if name is not None:
                name = name.strip()
                if not name:
                    raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
                other = (
                    db.query(Grammage)
                    .filter(Grammage.name == name, Grammage.id != row.id)
                    .first()
                )
                if other:
                    raise HTTPException(status_code=400, detail="Ya existe un gramaje con ese nombre")
                row.name = name
            if alias is not None:
                row.alias = alias.strip()
            if tolerance is not None:
                row.tolerance = tolerance.strip()
            if url is not None:
                row.url = url.strip() or None
            if status is not None:
                row.status = status
            db.commit()
            db.refresh(row)
            return GrammageController._to_dict(row)

    @staticmethod
    def delete(grammage_id: int):
        with SessionLocal() as db:
            row = db.query(Grammage).filter(Grammage.id == grammage_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Gramaje no encontrado")
            in_use = (
                db.query(ComplianceVerification)
                .filter(ComplianceVerification.grammage_id == grammage_id)
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
            return {"detail": "Gramaje eliminado"}
