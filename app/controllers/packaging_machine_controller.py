from fastapi import HTTPException
from app.models.parameters.packaging_machine import PackagingMachine
from app.lib.config.database import SessionLocal


class PackagingMachineController:
    @staticmethod
    def get_all():
        """
        Obtiene todas las máquinas de empaque.
        """
        db = SessionLocal()
        try:
            products = (
                db.query(PackagingMachine)
                .filter(PackagingMachine.status == 1)
                .order_by(PackagingMachine.id)
                .all()
            )
            return {
                "data": products,
                "message": "Máquinas de empaque obtenidas exitosamente",
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener máquinas de empaque: {str(e)}",
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(packaging_machine_id: int):
        """
        Obtiene una máquinas de empaque por su ID.
        """
        db = SessionLocal()
        try:
            packaging_machine = (
                db.query(PackagingMachine)
                .filter(
                    PackagingMachine.id == packaging_machine_id,
                    PackagingMachine.status == 1,
                )
                .first()
            )
            if not packaging_machine:
                raise HTTPException(
                    status_code=404, detail="Máquina de empaque no encontrada"
                )
            return packaging_machine
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener máquina de empaque: {str(e)}"
            )
        finally:
            db.close()

    def create_packaging_machine(self, packaging_machine_data: PackagingMachine):
        """
        Crea una nueva máquina de empaque.
        """
        db = SessionLocal()
        try:
            new_packaging_machine = PackagingMachine(**packaging_machine_data.dict())
            db.add(new_packaging_machine)
            db.commit()
            db.refresh(new_packaging_machine)
            return new_packaging_machine
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear máquina de empaque: {str(e)}"
            )
        finally:
            db.close()
