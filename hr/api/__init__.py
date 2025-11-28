from ninja import NinjaAPI
from .v1 import v1_router

# Create main API instance
api = NinjaAPI(
    title='BOMACH HR API',
    version='1.0.0',
    description='API for BOMACH HR Management System',
)

# Add version routers
api.add_router('/v1', v1_router)

__all__ = ['api']
