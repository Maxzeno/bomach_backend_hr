from typing import List, Optional
from ninja import Router, Query
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from hr.models.asset import Asset
from hr.api.schemas.asset import AssetCreate, AssetUpdate, AssetOut

router = Router()

@router.get("/", response=List[AssetOut])
@paginate(LimitOffsetPagination, page_size=10)
def list_assets(
    request,
    search: Optional[str] = None,
    branch: Optional[str] = None,
    asset_type: Optional[str] = None,
    status: Optional[str] = None
):
    qs = Asset.objects.all()

    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(asset_id__icontains=search))

    if branch:
        qs = qs.filter(branch=branch)

    if asset_type:
        qs = qs.filter(asset_type=asset_type)

    if status:
        qs = qs.filter(status=status)

    return qs

@router.post("/", response=AssetOut)
def create_asset(request, payload: AssetCreate):
    asset = Asset.objects.create(**payload.model_dump())
    return asset

@router.get("/{asset_id}", response=AssetOut)
def get_asset(request, asset_id: int):
    asset = get_object_or_404(Asset, id=asset_id)
    return asset

@router.put("/{asset_id}", response=AssetOut)
def update_asset(request, asset_id: int, payload: AssetUpdate):
    asset = get_object_or_404(Asset, id=asset_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, attr, value)
    asset.save()
    return asset

@router.delete("/{asset_id}")
def delete_asset(request, asset_id: int):
    asset = get_object_or_404(Asset, id=asset_id)
    asset.delete()
    return {"detail": "Deleted successfully"}
