from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.auth.routes import router as auth_router
from app.auth.dependencies import get_current_user
from app.core.ratelimit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.config import UPLOAD_DIR

from app.api.routes.templates import router as template_router
from app.api.routes.projects import router as project_router
from app.api.routes.hierarchy import router as hierarchy_router
from app.api.routes.assets import router as asset_router
from app.api.routes.images import router as images_router
from app.api.routes.categories import router as categories_router
from app.api.routes.task import router as task_router
from app.api.routes.variant import router as variant_router
from app.api.routes.publish_types import router as publish_types_router
from app.api.routes.episode import router as episode_router
from app.api.routes.sequence import router as sequence_router
from app.api.routes.shot import router as shots_router
from app.api.routes.domains import router as domain_router
from app.api.routes.editorial import router as editorial_router
from app.api.routes.library import router as library_router
from app.api.routes.cycle import router as cycle_router
from app.api.routes.versions import router as versions_router
from app.api.routes.users import router as users_router
from app.api.routes.media import router as media_router
from app.api.routes.reviews import router as reviews_router

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Tenant Backend API",
    description="API for tenant management",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://test.localhost:5173",  # Add this if you're using test.localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Add this to expose headers
)

# Include routers

app.include_router(auth_router, prefix="/api/v1")
app.include_router(template_router, prefix="/api/v1/template", tags=["Template"])
app.include_router(project_router, prefix="/api/v1/projects", tags=["project"])
app.include_router(hierarchy_router, prefix="/api/v1/hierarchy", tags=["hierarchy"])
app.include_router(asset_router, prefix="/api/v1/assets", tags=['assets'])
app.include_router(images_router, prefix="/api/v1/images", tags=["images"])
app.include_router(categories_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(variant_router, prefix="/api/v1/variants", tags=["variants"])
app.include_router(publish_types_router, prefix="/api/v1/publish_type")
app.include_router(episode_router, prefix="/api/v1/episode")
app.include_router(sequence_router, prefix="/api/v1")
app.include_router(shots_router, prefix="/api/v1")
app.include_router(domain_router, prefix="/api/v1/domains", tags=["domains"])
app.include_router(editorial_router, prefix="/api/v1/editorial", tags=["editorial"])
app.include_router(library_router, prefix="/api/v1/library", tags=["library"])
app.include_router(cycle_router, prefix="/api/v1/cycle", tags=["cycle"])
app.include_router(versions_router, prefix="/api/v1/versions", tags=["versions"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(media_router, prefix="/api/v1/media", tags=["media"])
app.include_router(reviews_router, prefix="/api/v1/reviews", tags=["reviews"])
from app.api.routes.api_tokens import router as api_tokens_router
app.include_router(api_tokens_router, prefix="/api/v1/api_tokens", tags=["api_tokens"])





app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

@app.get("/")
async def root():
    return {
        "message": "Tenant Backend API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    """Example protected route that requires authentication."""
    return {
        "message": "This is a protected endpoint",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": f"{current_user.first_name} {current_user.last_name}"
        }
    }