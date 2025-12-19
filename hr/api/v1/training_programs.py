from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, Query
from hr.models import TrainingProgram
from hr.api.schemas import (
    TrainingProgramCreateSchema,
    TrainingProgramUpdateSchema,
    TrainingProgramResponseSchema,
    TrainingProgramListSchema,
    TrainingProgramFilterSchema,
)
from ninja.pagination import paginate

router = Router(tags=['Training Programs'])


@router.post("/", response={201: TrainingProgramResponseSchema})
def create_training_program(request, payload: TrainingProgramCreateSchema):
    """Create a new training program"""
    program = TrainingProgram.objects.create(**payload.model_dump())
    return 201, program


@router.get("/", response=List[TrainingProgramListSchema])
@paginate
def list_training_programs(
    request,
    search: Optional[str] = Query(None, description="Search by program name"),
    filters: TrainingProgramFilterSchema = Query(...)
):
    """List all training programs with search and filters"""
    programs = TrainingProgram.objects.all()

    # Search functionality (by program name)
    if search:
        programs = programs.filter(program_name__icontains=search)

    # Filters from schema
    if filters.program_name:
        programs = programs.filter(program_name__icontains=filters.program_name)
    if filters.provider:
        programs = programs.filter(provider__icontains=filters.provider)
    if filters.status:
        programs = programs.filter(status=filters.status)
    if filters.target_audience:
        programs = programs.filter(target_audience=filters.target_audience)
    if filters.start_date_from:
        programs = programs.filter(start_date__gte=filters.start_date_from)
    if filters.start_date_to:
        programs = programs.filter(start_date__lte=filters.start_date_to)
    if filters.end_date_from:
        programs = programs.filter(end_date__gte=filters.end_date_from)
    if filters.end_date_to:
        programs = programs.filter(end_date__lte=filters.end_date_to)
    if filters.min_cost:
        programs = programs.filter(cost__gte=filters.min_cost)
    if filters.max_cost:
        programs = programs.filter(cost__lte=filters.max_cost)

    return programs


@router.get("/{program_id}", response=TrainingProgramResponseSchema)
def get_training_program(request, program_id: int):
    """Get a single training program by ID"""
    program = get_object_or_404(TrainingProgram, id=program_id)
    return program


@router.put("/{program_id}", response=TrainingProgramResponseSchema)
def update_training_program(request, program_id: int, payload: TrainingProgramUpdateSchema):
    """Update a training program"""
    program = get_object_or_404(TrainingProgram, id=program_id)

    update_data = payload.model_dump(exclude_unset=True)

    # Validate date logic if both dates are being updated
    if 'start_date' in update_data and 'end_date' in update_data:
        if update_data['end_date'] < update_data['start_date']:
            raise ValueError('End date must be after start date')
    elif 'start_date' in update_data and update_data['start_date'] > program.end_date:
        raise ValueError('Start date cannot be after current end date')
    elif 'end_date' in update_data and update_data['end_date'] < program.start_date:
        raise ValueError('End date cannot be before current start date')

    for attr, value in update_data.items():
        setattr(program, attr, value)

    program.save()
    return program


@router.patch("/{program_id}/status", response=TrainingProgramResponseSchema)
def update_training_program_status(request, program_id: int, status: str = Query(...)):
    """Update only the status of a training program"""
    program = get_object_or_404(TrainingProgram, id=program_id)

    valid_statuses = ['Pending', 'In Progress', 'Completed', 'Cancelled']
    if status not in valid_statuses:
        raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')

    program.status = status
    program.save()
    return program


@router.delete("/{program_id}", response={204: None})
def delete_training_program(request, program_id: int):
    """Delete a training program"""
    program = get_object_or_404(TrainingProgram, id=program_id)
    program.delete()
    return 204, None
