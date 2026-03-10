from fastapi import HTTPException
from app.models.parameters.units_packed_hour import UnitsPackedHour
from app.lib.config.database import SessionLocal


class UnitsPackedHourController:
    @staticmethod
    def get_all():
        """
        Obtiene todos los unidades empaquetadas por hora.
        """
        db = SessionLocal()
        try:
            units_packed_hour = (
                db.query(UnitsPackedHour)
                .filter(UnitsPackedHour.status == 1)
                .order_by(UnitsPackedHour.id)
                .all()
            )
            return {
                "data": units_packed_hour,
                "message": "Unidades empaquetadas por hora obtenidas exitosamente",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener unidades empaquetadas por hora: {str(e)}",
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(units_packed_hour_id: int):
        """
        Obtiene una unidad empaquetada por hora por su ID.
        """
        db = SessionLocal()
        try:
            units_packed_hour = (
                db.query(UnitsPackedHour)
                .filter(
                    UnitsPackedHour.id == units_packed_hour_id,
                    UnitsPackedHour.status == 1,
                )
                .first()
            )
            if not units_packed_hour:
                raise HTTPException(
                    status_code=404, detail="Unidad empaquetada por hora no encontrada"
                )
            return units_packed_hour
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener unidad empaquetada por hora: {str(e)}",
            )
        finally:
            db.close()

    def create_units_packed_hour(self, units_packed_hour_data: UnitsPackedHour):
        """
        Crea una nueva unidad empaquetada por hora.
        """
        db = SessionLocal()
        try:
            new_units_packed_hour = UnitsPackedHour(**units_packed_hour_data.dict())
            db.add(new_units_packed_hour)
            db.commit()
            db.refresh(new_units_packed_hour)
            return new_units_packed_hour
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear gramaje: {str(e)}"
            )
        finally:
            db.close()
