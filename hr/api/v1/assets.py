from typing import List, Optional
from ninja import Router, Query
from django.shortcuts import get_object_or_404
from uuid import UUID
from hr.models.asset import Asset
from hr.api.schemas.asset import AssetCreate, AssetUpdate, AssetOut

router = Router()

@router.get("/", response=List[AssetOut])
def list_assets(
    request,
    search: Optional[str] = None,
    branch: Optional[str] = None,
    asset_type: Optional[str] = None,
    status: Optional[str] = None
):
    qs = Asset.objects.all()
    
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(asset_id__icontains=search)
    
    if branch:
        qs = qs.filter(branch=branch)
        
    if asset_type:
        qs = qs.filter(asset_type=asset_type)
        
    if status:
        qs = qs.filter(status=status)
        
    return qs

@router.post("/", response=AssetOut)
def create_asset(request, payload: AssetCreate):
    asset = Asset.objects.create(**payload.dict())
    return asset

@router.get("/{asset_id}", response=AssetOut)
def get_asset(request, asset_id: UUID):
    asset = get_object_or_404(Asset, id=asset_id)
    return asset

@router.put("/{asset_id}", response=AssetOut)
def update_asset(request, asset_id: UUID, payload: AssetUpdate):
    asset = get_object_or_404(Asset, id=asset_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(asset, attr, value)
    asset.save()
    return asset

@router.delete("/{asset_id}")
def delete_asset(request, asset_id: UUID):
    asset = get_object_or_404(Asset, id=asset_id)
    asset.delete()
    return {"success": True}
