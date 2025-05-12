from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.endpoints import content, posts

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered social media content generation and publishing platform",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include routers
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])

# Import and include routers
# Will be implemented as we build each module
# from app.api.endpoints import content, images, scheduler, etc.
# app.include_router(content.router, prefix="/api/content", tags=["content"])
# app.include_router(images.router, prefix="/api/images", tags=["images"])
# and so on... 