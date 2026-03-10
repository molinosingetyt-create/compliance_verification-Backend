from fastapi import HTTPException
from app.models.parameters.lot_size import LotSize
from app.lib.config.database import SessionLocal


class LotSizeController:
    @staticmethod
    def get_all():
        """
        Obtiene todos los tamaños de lote.
        """
        db = SessionLocal()
        try:
            lot_sizes = (
                db.query(LotSize).filter(LotSize.status == 1).order_by(LotSize.id).all()
            )
            return {
                "data": lot_sizes,
                "message": "Tamaños de lote obtenidos exitosamente",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener tamaños de lote: {str(e)}",
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(lot_size_id: int):
        """
        Obtiene un tamaño de lote por su ID.
        """
        db = SessionLocal()
        try:
            lot_size = (
                db.query(LotSize)
                .filter(
                    LotSize.id == lot_size_id,
                    LotSize.status == 1,
                )
                .first()
            )
            if not lot_size:
                raise HTTPException(
                    status_code=404, detail="Tamaño de lote no encontrado"
                )
            return lot_size
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener tamaño de lote: {str(e)}",
            )
        finally:
            db.close()

    def create_lot_size(self, lot_size_data: LotSize):
        """
        Crea un nuevo tamaño de lote.
        """
        db = SessionLocal()
        try:
            new_lot_size = LotSize(**lot_size_data.dict())
            db.add(new_lot_size)
            db.commit()
            db.refresh(new_lot_size)
            return new_lot_size
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear tamaño de lote: {str(e)}"
            )
        finally:
            db.close()
