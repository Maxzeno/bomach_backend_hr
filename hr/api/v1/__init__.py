from ninja import Router
from .departments import router as departments_router
from .sub_departments import router as sub_departments_router
from .job_postings import router as job_postings_router
from .applicants import router as applicants_router
from .leave_requests import router as leave_requests_router
from .performance_reviews import router as performance_reviews_router
from .payroll import router as payroll_router
from .training_programs import router as training_programs_router
from .associates import router as associates_router
from .assets import router as assets_router

# Create v1 router
v1_router = Router()

# Add sub-routers
v1_router.add_router('/departments', departments_router)
v1_router.add_router('/sub-departments', sub_departments_router)
v1_router.add_router('/job-postings', job_postings_router)
v1_router.add_router('/applicants', applicants_router)
v1_router.add_router('/leave-requests', leave_requests_router)
v1_router.add_router('/performance-reviews', performance_reviews_router)
v1_router.add_router('/payroll', payroll_router)
v1_router.add_router('/training-programs', training_programs_router)
v1_router.add_router('/associates', associates_router)
v1_router.add_router('/assets', assets_router)

__all__ = ['v1_router']
