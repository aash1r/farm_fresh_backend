from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import logging

from app.routers import products, users, orders, auth, delivery, payments, files
from app.core.config import settings
# from app.db.init_app import init as init_db
from app.db.session import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Farm Fresh Shop API",
    description="API for Farm Fresh Shop application",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    version="1.0.0",
    redirect_slashes=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Initialize database on startup
# @app.on_event("startup")
# def startup_db_client():
#     logger.info("Initializing database")
#     init_db()
#     logger.info("Database initialized")

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(orders.router, prefix="/api/v1", tags=["Orders"])
app.include_router(delivery.router, prefix="/api/v1", tags=["Delivery"])
app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])
app.include_router(files.router, prefix="/api/v1", tags=["Files"])

@app.get("/api/v1", tags=["Root"])
async def root():
    return {"message": "Welcome to Farm Fresh Shop API"}

# Handler for AWS Lambda
# handler = Mangum(app)
