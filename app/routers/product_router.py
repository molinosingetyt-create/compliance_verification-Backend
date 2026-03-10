from fastapi import APIRouter, Depends, Query
from app.controllers.product_controller import ProductController
from app.forms.product_form import CreateProductForm
from app.lib.config.database import get_db
from app.schemas.response_schemas import (
    ProductResponse,
    ProductListResponse,
    BadRequestResponse,
    NotFoundResponse,
    InternalServerErrorResponse,
)

router = APIRouter()


@router.get(
    "/list/all",
    tags=["products"],
    response_model=ProductListResponse,
    responses={
        200: {
            "description": "Productos obtenidos exitosamente",
            "model": ProductListResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_all_products():
    """
    Obtiene todos los productos.

    **Respuestas:**
    - **200**: Retorna lista de productos exitosamente
    - **500**: Error al consultar la base de datos
    """
    return ProductController.get_all()


@router.get(
    "/list",
    tags=["products"],
    response_model=ProductResponse,
    responses={
        200: {
            "description": "Producto obtenido exitosamente",
            "model": ProductResponse,
        },
        404: {
            "description": "Producto no encontrado",
            "model": NotFoundResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_product_by_id(id: int = Query(..., description="ID del producto")):
    """
    Obtiene un producto por su ID.

    **Parámetros:**
    - **id**: ID único del producto

    **Respuestas:**
    - **200**: Producto encontrado y retornado exitosamente
    - **404**: No existe un producto con el ID proporcionado
    - **500**: Error al consultar la base de datos
    """
    return ProductController.get_by_id(id)


@router.post(
    "/create",
    tags=["products"],
    response_model=ProductResponse,
    responses={
        200: {
            "description": "Producto creado exitosamente",
            "model": ProductResponse,
        },
        400: {
            "description": "Solicitud inválida - Campos requeridos faltantes",
            "model": BadRequestResponse,
        },
        500: {
            "description": "Error interno del servidor",
            "model": InternalServerErrorResponse,
        },
    },
)
async def create_product(product_data: CreateProductForm):
    """
    Crea un nuevo producto.

    **Request Body:**
    - **name** (str): Nombre del producto
    - **alias** (str): Alias del producto

    **Respuestas:**
    - **200**: Producto creado exitosamente
    - **400**: Datos inválidos o campos requeridos faltantes
    - **500**: Error al crear el producto en la base de datos
    """
    controller = ProductController()
    return controller.create_product(product_data)
