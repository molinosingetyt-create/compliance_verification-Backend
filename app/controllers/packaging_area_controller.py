from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.parameters.packaging_area import PackagingArea
from app.models.parameters.packaging_machine import PackagingMachine
from app.models.user import User
from app.lib.config.database import SessionLocal


class PackagingAreaController:
    @staticmethod
    def _to_dict(row: PackagingArea) -> dict:
        return row.toDict()

    @staticmethod
    def list_active():
        with SessionLocal() as db:
            rows = (
                db.query(PackagingArea)
                .filter(PackagingArea.status == 1)
                .order_by(PackagingArea.id.asc())
                .all()
            )
            return {"data": [PackagingAreaController._to_dict(r) for r in rows]}

    @staticmethod
    def list_all():
        with SessionLocal() as db:
            rows = db.query(PackagingArea).order_by(PackagingArea.id.asc()).all()
            return [PackagingAreaController._to_dict(r) for r in rows]

    @staticmethod
    def get_by_id(packaging_area_id: int, include_inactive: bool = False):
        with SessionLocal() as db:
            q = db.query(PackagingArea).filter(PackagingArea.id == packaging_area_id)
            if not include_inactive:
                q = q.filter(PackagingArea.status == 1)
            row = q.first()
            if not row:
                raise HTTPException(status_code=404, detail="Área de empaque no encontrada")
            return PackagingAreaController._to_dict(row)

    @staticmethod
    def create(name: str, alias: str):
        name = (name or "").strip()
        alias = (alias or "").strip()
        if not name or not alias:
            raise HTTPException(status_code=400, detail="Nombre y alias son obligatorios")
        with SessionLocal() as db:
            if db.query(PackagingArea).filter(PackagingArea.name == name).first():
                raise HTTPException(status_code=400, detail="Ya existe un área con ese nombre")
            row = PackagingArea(name=name, alias=alias, status=1)
            db.add(row)
            db.commit()
            db.refresh(row)
            return PackagingAreaController._to_dict(row)

    @staticmethod
    def update(packaging_area_id: int, name: Optional[str] = None, alias: Optional[str] = None):
        with SessionLocal() as db:
            row = db.query(PackagingArea).filter(PackagingArea.id == packaging_area_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Área de empaque no encontrada")
            if name is not None:
                name = name.strip()
                if not name:
                    raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
                other = (
                    db.query(PackagingArea)
                    .filter(PackagingArea.name == name, PackagingArea.id != row.id)
                    .first()
                )
                if other:
                    raise HTTPException(status_code=400, detail="Ya existe un área con ese nombre")
                row.name = name
            if alias is not None:
                alias = alias.strip()
                if not alias:
                    raise HTTPException(status_code=400, detail="El alias no puede estar vacío")
                row.alias = alias
            db.commit()
            db.refresh(row)
            return PackagingAreaController._to_dict(row)

    @staticmethod
    def delete(packaging_area_id: int):
        with SessionLocal() as db:
            row = db.query(PackagingArea).filter(PackagingArea.id == packaging_area_id).first()
            if not row:
                raise HTTPException(status_code=404, detail="Área de empaque no encontrada")
            machines = (
                db.query(PackagingMachine)
                .filter(PackagingMachine.packaging_area_id == packaging_area_id)
                .count()
            )
            if machines > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede eliminar: {machines} máquina(s) usan esta área",
                )
            users = db.query(User).filter(User.packaging_area_id == packaging_area_id).count()
            if users > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede eliminar: {users} usuario(s) tienen asignada esta área",
                )
            row.status = 0
            db.commit()
            return {"detail": "Área eliminada"}
