from fastapi import APIRouter, Depends, Query

from app.controllers.grammage_controller import GrammageController
from app.forms.grammage_form import CreateGrammageForm, UpdateGrammageForm
from app.lib.security.deps import get_current_user, require_permission

router = APIRouter()
_manage = Depends(require_permission("catalog:manage"))


@router.get("/list/all", tags=["grammage"])
async def get_all_grammages(_user=Depends(get_current_user)):
    return GrammageController.list_active()


@router.get("/manage", tags=["grammage"], dependencies=[_manage])
async def manage_list_grammages():
    return GrammageController.list_all()


@router.get("/list", tags=["grammage"])
async def get_grammage_by_id(
    id: int = Query(..., description="ID del gramaje"),
    _user=Depends(get_current_user),
):
    return GrammageController.get_by_id(id)


@router.get("/{grammage_id}", tags=["grammage"], dependencies=[_manage])
async def get_grammage_by_path_id(grammage_id: int):
    return GrammageController.get_by_id(grammage_id, include_inactive=True)


@router.post("/create", tags=["grammage"], dependencies=[_manage])
async def create_grammage(grammage_data: CreateGrammageForm):
    return GrammageController.create(
        grammage_data.name,
        grammage_data.alias,
        grammage_data.tolerance,
        grammage_data.url,
    )


@router.put("/{grammage_id}", tags=["grammage"], dependencies=[_manage])
async def update_grammage(grammage_id: int, body: UpdateGrammageForm):
    return GrammageController.update(
        grammage_id, body.name, body.alias, body.tolerance, body.url
    )


@router.delete("/{grammage_id}", tags=["grammage"], dependencies=[_manage])
async def delete_grammage(grammage_id: int):
    return GrammageController.delete(grammage_id)
