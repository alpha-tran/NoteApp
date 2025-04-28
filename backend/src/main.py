from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import logging # Import logging
from pymongo import ASCENDING, IndexModel # Import for index creation
import time
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from routes import auth, users, notes  # Import new routers
from database import DataBase # Import MongoDB class
from logging_config import setup_logging
from middleware.security import setup_security_middleware, SecurityMiddleware
from middleware import security
from schemas import user
from infrastructure.database import Database

# Setup logging before creating the app instance
setup_logging()

logger = logging.getLogger(__name__) # Get logger for main module

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Secure Note-Taking Application API",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Security middleware
app.add_middleware(SecurityMiddleware)

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=settings.SESSION_LIFETIME,
    same_site="lax",
    https_only=settings.ENVIRONMENT != "development"
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    
    await Database.connect_to_database()
    
    try:
        db = Database.db
        
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
    await Database.close_database_connection()
    logger.info("Application shutdown events completed")

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(notes.router, prefix=settings.API_V1_STR, tags=["notes"])

# Add global OPTIONS route handler
@app.options("/{full_path:path}")
async def options_route(request: Request, full_path: str):
    return {}

@app.get(f"{settings.API_V1_STR}/health")
async def health_check_v1():
    """Health check endpoint (v1)"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }

@app.get("/")
async def root():
    return {"message": "Welcome to NoteApp API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        ssl_keyfile=settings.SSL_KEYFILE if settings.USE_HTTPS else None,
        ssl_certfile=settings.SSL_CERTFILE if settings.USE_HTTPS else None
    )