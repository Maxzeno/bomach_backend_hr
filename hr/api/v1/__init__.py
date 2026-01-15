from ninja import Router
from .job_postings import router as job_postings_router
from .applicants import router as applicants_router
from .leave_requests import router as leave_requests_router
from .performance_reviews import router as performance_reviews_router
from .payroll import router as payroll_router
from .training_programs import router as training_programs_router
from .associates import router as associates_router
from .assets import router as assets_router
from .award import router as award_router
from .work_reports import router as work_reports_router
from ninja.errors import ValidationError
from django.http import JsonResponse


# Create v1 router
v1_router = Router()

# Add sub-routers
v1_router.add_router('/job-postings', job_postings_router)
v1_router.add_router('/applicants', applicants_router)
v1_router.add_router('/leave-requests', leave_requests_router)
v1_router.add_router('/performance-reviews', performance_reviews_router)
v1_router.add_router('/payroll', payroll_router)
v1_router.add_router('/training-programs', training_programs_router)
v1_router.add_router('/associates', associates_router)
v1_router.add_router('/assets', assets_router)
v1_router.add_router('/awards', award_router)
v1_router.add_router('/work-reports', work_reports_router)
