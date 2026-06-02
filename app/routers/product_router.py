from fastapi import APIRouter, Depends, Query

from app.controllers.product_controller import ProductController
from app.forms.product_form import CreateProductForm, UpdateProductForm
from app.lib.security.deps import get_current_user, require_permission

router = APIRouter()
_manage = Depends(require_permission("catalog:manage"))


@router.get("/list/all", tags=["products"])
async def get_all_products(_user=Depends(get_current_user)):
    """Listado activo para muestreo y selects."""
    return ProductController.list_active()


@router.get("/manage", tags=["products"], dependencies=[_manage])
async def manage_list_products():
    """Listado completo para administración (ID ascendente)."""
    return ProductController.list_all()


@router.get("/list", tags=["products"])
async def get_product_by_id(
    id: int = Query(..., description="ID del producto"),
    _user=Depends(get_current_user),
):
    return ProductController.get_by_id(id)


@router.get("/{product_id}", tags=["products"], dependencies=[_manage])
async def get_product_by_path_id(product_id: int):
    return ProductController.get_by_id(product_id, include_inactive=True)


@router.post("/create", tags=["products"], dependencies=[_manage])
async def create_product(product_data: CreateProductForm):
    return ProductController.create(
        product_data.name, product_data.alias, product_data.url
    )


@router.put("/{product_id}", tags=["products"], dependencies=[_manage])
async def update_product(product_id: int, body: UpdateProductForm):
    return ProductController.update(
        product_id, body.name, body.alias, body.url
    )


@router.delete("/{product_id}", tags=["products"], dependencies=[_manage])
async def delete_product(product_id: int):
    return ProductController.delete(product_id)
