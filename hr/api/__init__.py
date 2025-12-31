from ninja import NinjaAPI, Swagger
from .v1 import v1_router
from hr.utils.auth import AuthBearer

# Create main API instance with authentication
api = NinjaAPI(
    title='BOMACH HR API',
    version='1.0.0',
    description='API for BOMACH HR Management System',
    docs_url='v1/docs/',
    docs=Swagger(settings={"persistAuthorization": True}),
    auth=AuthBearer(),  # Require authentication for all endpoints by default
)

# Add version routers
api.add_router('/v1', v1_router)

__all__ = ['api']
