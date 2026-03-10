from fastapi import HTTPException
from app.models.parameters.grammage import Grammage
from app.lib.config.database import SessionLocal


class GrammageController:
    @staticmethod
    def get_all():
        """
        Obtiene todos los gramajes.
        """
        db = SessionLocal()
        try:
            grammage = (
                db.query(Grammage)
                .filter(Grammage.status == 1)
                .order_by(Grammage.id)
                .all()
            )
            return {
                "data": grammage,
                "message": "Gramajes obtenidos exitosamente",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener gramajes: {str(e)}",
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(grammage_id: int):
        """
        Obtiene un gramaje por su ID.
        """
        db = SessionLocal()
        try:
            grammage = (
                db.query(Grammage)
                .filter(
                    Grammage.id == grammage_id,
                    Grammage.status == 1,
                )
                .first()
            )
            if not grammage:
                raise HTTPException(status_code=404, detail="Gramaje no encontrado")
            return grammage
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener gramaje: {str(e)}"
            )
        finally:
            db.close()

    def create_grammage(self, grammage_data: Grammage):
        """
        Crea un nuevo gramaje.
        """
        db = SessionLocal()
        try:
            new_grammage = Grammage(**grammage_data.dict())
            db.add(new_grammage)
            db.commit()
            db.refresh(new_grammage)
            return new_grammage
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear gramaje: {str(e)}"
            )
        finally:
            db.close()
