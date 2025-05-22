from typing import Optional
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Message describing the result")
    file_url: Optional[str] = Field(None, description="URL of the uploaded file if successful")
