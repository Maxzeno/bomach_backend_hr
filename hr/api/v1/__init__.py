from ninja import Router
from .departments import router as departments_router
from .sub_departments import router as sub_departments_router
from .job_postings import router as job_postings_router

# Create v1 router
v1_router = Router()

# Add sub-routers
v1_router.add_router('/departments', departments_router)
v1_router.add_router('/sub-departments', sub_departments_router)
v1_router.add_router('/job-postings', job_postings_router)

__all__ = ['v1_router']
