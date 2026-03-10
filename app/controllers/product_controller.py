from fastapi import HTTPException
from app.models.parameters.product import Product
from app.lib.config.database import SessionLocal


class ProductController:
    @staticmethod
    def get_all():
        """
        Obtiene todos los productos.
        """
        db = SessionLocal()
        try:
            products = (
                db.query(Product).filter(Product.status == 1).order_by(Product.id).all()
            )
            return {"data": products, "message": "Productos obtenidos exitosamente"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener productos: {str(e)}"
            )
        finally:
            db.close()

    @staticmethod
    def get_by_id(product_id: int):
        """
        Obtiene un producto por su ID.
        """
        db = SessionLocal()
        try:
            product = (
                db.query(Product)
                .filter(Product.id == product_id, Product.status == 1)
                .first()
            )
            if not product:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return product
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error al obtener producto: {str(e)}"
            )
        finally:
            db.close()

    def create_product(self, product_data: Product):
        """
        Crea un nuevo producto.
        """
        db = SessionLocal()
        try:
            new_product = Product(**product_data.dict())
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return new_product
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear producto: {str(e)}"
            )
        finally:
            db.close()
