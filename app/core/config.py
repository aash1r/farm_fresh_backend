import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Farm Fresh Shop API"
    
    # CORS Origins
    
    # Database settings
    DATABASE_URL: str = ""
    
    # JWT settings
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    
    # AWS S3 settings for product images
    # AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    # AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    # AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    # AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME", "farm-fresh-shop-images")
    
    class Config:
        env_file = ".env"

settings = Settings()
