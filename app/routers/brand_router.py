from fastapi import APIRouter, Depends, Query

from app.controllers.brand_controller import BrandController
from app.forms.brand_form import CreateBrandForm, UpdateBrandForm
from app.lib.security.deps import get_current_user, require_permission

router = APIRouter()
_manage = Depends(require_permission("catalog:manage"))


@router.get("/list/all", tags=["brands"])
async def get_all_brands(_user=Depends(get_current_user)):
    return BrandController.list_active()


@router.get("/manage", tags=["brands"], dependencies=[_manage])
async def manage_list_brands():
    return BrandController.list_all()


@router.get("/list", tags=["brands"])
async def get_brand_by_id(
    id: int = Query(..., description="ID de la marca"),
    _user=Depends(get_current_user),
):
    return BrandController.get_by_id(id)


@router.get("/{brand_id}", tags=["brands"], dependencies=[_manage])
async def get_brand_by_path_id(brand_id: int):
    return BrandController.get_by_id(brand_id, include_inactive=True)


@router.post("/create", tags=["brands"], dependencies=[_manage])
async def create_brand(brand_data: CreateBrandForm):
    return BrandController.create(brand_data.name, brand_data.alias, brand_data.url)


@router.put("/{brand_id}", tags=["brands"], dependencies=[_manage])
async def update_brand(brand_id: int, body: UpdateBrandForm):
    return BrandController.update(brand_id, body.name, body.alias, body.url)


@router.delete("/{brand_id}", tags=["brands"], dependencies=[_manage])
async def delete_brand(brand_id: int):
    return BrandController.delete(brand_id)
