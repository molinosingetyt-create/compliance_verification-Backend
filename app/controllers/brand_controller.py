from fastapi import HTTPException
from app.models.parameters.brand import Brand
from app.lib.config.database import SessionLocal


class BrandController:
    @staticmethod
    def get_all():
        """
        Obtiene todas las marcas.
        """
        db = SessionLocal()
        try:
            brands = db.query(Brand).filter(Brand.status == 1).order_by(Brand.id).all()
            return {"data": brands, "message": "Marcas obtenidas exitosamente"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener marcas: {str(e)}"
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(brand_id: int):
        """
        Obtiene una marca por su ID.
        """
        db = SessionLocal()
        try:
            brand = (
                db.query(Brand).filter(Brand.id == brand_id, Brand.status == 1).first()
            )
            if not brand:
                raise HTTPException(status_code=404, detail="Marca no encontrada")
            return brand
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener marca: {str(e)}"
            )
        finally:
            db.close()

    def create_brand(self, brand_data: Brand):
        """
        Crea un nueva marca.
        """
        db = SessionLocal()
        try:
            new_brand = Brand(**brand_data.dict())
            db.add(new_brand)
            db.commit()
            db.refresh(new_brand)
            return new_brand
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear marca: {str(e)}"
            )
        finally:
            db.close()
