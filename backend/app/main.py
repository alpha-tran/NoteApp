from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import logging # Import logging
from pymongo import ASCENDING, IndexModel # Import for index creation
import time

from .config import settings
from .routes import auth, users, notes  # Import new routers
from .database import connect_to_mongo, close_mongo_connection, get_mongo_db # Import MongoDB functions
from .logging_config import setup_logging
from .middleware.security import setup_security_middleware

# Setup logging before creating the app instance
setup_logging()

logger = logging.getLogger(__name__) # Get logger for main module

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs" if not settings.is_production() else None,
    redoc_url="/api/redoc" if not settings.is_production() else None,
    openapi_url="/api/openapi.json" if not settings.is_production() else None,
    swagger_ui_oauth2_redirect_url=None,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.CLIENT_ID if settings.is_production() else None
    }
)

# Setup all security middleware
setup_security_middleware(app)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Preflight cache duration in seconds (24 hours)
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB, validate settings, and create indexes on startup"""
    logger.info("Starting application startup events...")
    
    # Validate environment
    if settings.is_production():
        if settings.DEBUG:
            raise ValueError("DEBUG must be False in production")
        if not settings.SSL_CERTFILE or not settings.SSL_KEYFILE:
            raise ValueError("SSL certificates must be configured in production")
    
    await connect_to_mongo()
    
    try:
        db = get_mongo_db()
        
        # User indexes
        user_collection = db["users"]
        await user_collection.create_indexes([
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("username", ASCENDING)], unique=True),
            IndexModel([("last_login", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)])
        ])
        logger.info("Indexes created successfully for 'users' collection")
        
        # Note indexes
        note_collection = db["notes"]
        await note_collection.create_indexes([
            IndexModel([("owner_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
            IndexModel([("updated_at", ASCENDING)]),
            IndexModel([("title", "text"), ("content", "text")]),
            IndexModel([("is_public", ASCENDING)])
        ])
        logger.info("Indexes created successfully for 'notes' collection")
        
        # Session indexes
        session_collection = db["sessions"]
        await session_collection.create_indexes([
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0)
        ])
        logger.info("Indexes created successfully for 'sessions' collection")
        
    except Exception as e:
        logger.exception(f"Error creating indexes: {e}")
        raise

    logger.info("Application startup events completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    logger.info("Starting application shutdown events...")
    await close_mongo_connection()
    logger.info("Application shutdown events completed")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }