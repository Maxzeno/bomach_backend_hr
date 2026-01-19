from typing import List
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from hr.models.disciplinary_case import DisciplinaryCase
from hr.api.schemas.disciplinary_case import (
    DisciplinaryCaseSchema,
    DisciplinaryCaseCreateSchema,
    DisciplinaryCaseUpdateSchema,
)
from hr.api.schemas import MessageSchema

router = Router(tags=["Disciplinary Cases"])


@router.post("/", response={201: DisciplinaryCaseSchema, 400: MessageSchema})
def create_disciplinary_case(request, payload: DisciplinaryCaseCreateSchema):
    try:
        data = payload.model_dump(exclude_unset=True)
        case = DisciplinaryCase.objects.create(**data)
        return 201, case
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.get("/", response=List[DisciplinaryCaseSchema])
@paginate(LimitOffsetPagination, page_size=10)
def list_disciplinary_cases(
    request,
    employee_id: str = None,
    action_type: str = None,
    violation_category: str = None,
):
    qs = DisciplinaryCase.objects.all()
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if action_type:
        qs = qs.filter(action_type=action_type)
    if violation_category:
        qs = qs.filter(violation_category=violation_category)
    return qs


@router.get("/{case_id}", response=DisciplinaryCaseSchema)
def get_disciplinary_case(request, case_id: int):
    return get_object_or_404(DisciplinaryCase, id=case_id)


@router.put("/{case_id}", response={200: DisciplinaryCaseSchema, 400: MessageSchema})
def update_disciplinary_case(
    request, case_id: int, payload: DisciplinaryCaseUpdateSchema
):
    try:
        case = get_object_or_404(DisciplinaryCase, id=case_id)
        for attr, value in payload.model_dump(exclude_unset=True).items():
            setattr(case, attr, value)
        case.save()
        return 200, case
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}


@router.delete("/{case_id}", response={200: MessageSchema, 400: MessageSchema})
def delete_disciplinary_case(request, case_id: int):
    try:
        case = get_object_or_404(DisciplinaryCase, id=case_id)
        case.delete()
        return 200, {"detail": "Deleted successfully"}
    except ValidationError as e:
        return 400, {'detail': e.messages[0]}
