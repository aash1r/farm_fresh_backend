from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_admin_user, get_current_user
from app.models.user import User
from app.schemas.file import FileUploadResponse
from app.services.s3 import s3_service

router = APIRouter(prefix="/files")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    *,
    file: UploadFile = File(...),
    folder: str = Form("products"),  # Default folder is products
    current_user: User = Depends(get_current_admin_user),  # Only admins can upload files
) -> Any:
    """Upload a file to S3"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
        
    success, message, file_url = await s3_service.upload_file(file, folder)
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
        
    return FileUploadResponse(
        success=success,
        message=message,
        file_url=file_url
    )


@router.get("/list", response_model=List[dict])
async def list_files(
    *,
    prefix: str = Query("", description="Filter files by prefix"),
    current_user: User = Depends(get_current_admin_user),  # Only admins can list files
) -> Any:
    """List files in S3 bucket"""
    files = s3_service.list_files(prefix)
    return files


@router.delete("/{object_key:path}", response_model=FileUploadResponse)
async def delete_file(
    *,
    object_key: str,
    current_user: User = Depends(get_current_admin_user),  # Only admins can delete files
) -> Any:
    """Delete a file from S3"""
    success, message = s3_service.delete_file(object_key)
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
        
    return FileUploadResponse(
        success=success,
        message=message,
        file_url=None
    )
