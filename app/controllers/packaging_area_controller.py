from fastapi import HTTPException
from app.models.parameters.packaging_area import PackagingArea
from app.lib.config.database import SessionLocal


class PackagingAreaController:
    @staticmethod
    def get_all():
        """
        Obtiene todas las areas de empaque.
        """
        db = SessionLocal()
        try:
            products = (
                db.query(PackagingArea)
                .filter(PackagingArea.status == 1)
                .order_by(PackagingArea.id)
                .all()
            )
            return {
                "data": products,
                "message": "Áreas de empaque obtenidas exitosamente",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener áreas de empaque: {str(e)}"
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(packaging_area_id: int):
        """
        Obtiene un área de empaque por su ID.
        """
        db = SessionLocal()
        try:
            packaging_area = (
                db.query(PackagingArea)
                .filter(
                    PackagingArea.id == packaging_area_id,
                    PackagingArea.status == 1,
                )
                .first()
            )
            if not packaging_area:
                raise HTTPException(
                    status_code=404, detail="Área de empaque no encontrada"
                )
            return packaging_area
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener área de empaque: {str(e)}"
            )
        finally:
            db.close()

    def create_packaging_area(self, packaging_area_data: PackagingArea):
        """
        Crea una nueva área de empaque.
        """
        db = SessionLocal()
        try:
            new_packaging_area = PackagingArea(**packaging_area_data.dict())
            db.add(new_packaging_area)
            db.commit()
            db.refresh(new_packaging_area)
            return new_packaging_area
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear área de empaque: {str(e)}"
            )
        finally:
            db.close()
