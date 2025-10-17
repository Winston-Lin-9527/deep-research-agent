from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import os
from datetime import datetime

from src.database import get_db, DBDocument, DBUser
from src.pdf_vector_store_manager import pdf_vector_store_mgr
from src.pdf_vector_store_manager import PDFVectorStoreMgr
from src.auth import auth_handler, get_current_user

router = APIRouter()

# Request/Response models
class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    size: int
    upload_date: str
    status: str
 
class DocumentResponse(BaseModel):
    id: int
    doc_id: str
    original_filename: str
    file_size: int
    upload_date: datetime
    status: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]

# Authentication routes (keeping the previous implementation)
@router.post("/auth/register")
async def register_user(user_data: dict, db: Session = Depends(get_db)):
    """User registration endpoint"""
    email = user_data.get("email")
    password = user_data.get("password")
    name = user_data.get("name", "")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Check if user already exists
    existing_user = db.query(DBUser).filter(DBUser.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")
    
    # Create new user
    hashed_password = auth_handler.get_password_hash(password)
    db_user = DBUser(
        email=email,
        name=name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token_data = {"sub": str(db_user.id), "email": email}
    access_token = auth_handler.create_access_token(data=token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/login")
async def login_user(login_data: dict, db: Session = Depends(get_db)):
    """User login endpoint"""
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user or not auth_handler.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = auth_handler.create_access_token(data=token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me")
async def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user info"""
    user = db.query(DBUser).filter(DBUser.id == int(current_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "created_at": user.created_at
    }

# PDF upload route
@router.post("/upload/pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload and process PDF file"""
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Check file size (e.g., limit to 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")
    
    # Generate unique temp file name
    temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join("temp_uploads", temp_filename)
    
    # Create temp directory if it doesn't exist
    os.makedirs("temp_uploads", exist_ok=True)
    
    # Save uploaded file temporarily
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    try:
        # Process the PDF - this creates DB entry and vector store
        db_document = await pdf_vector_store_mgr.process_pdf(
            temp_path,
            file.filename,
            int(current_user_id),
            db
        )
        
        # Clean up temp file after processing
        background_tasks.add_task(
            lambda: os.remove(temp_path) if os.path.exists(temp_path) else None
        )
        
        return UploadResponse(
            doc_id=db_document.doc_id,
            filename=db_document.original_filename,
            size=db_document.file_size,
            upload_date=db_document.upload_date.isoformat(),
            status=db_document.status
        )
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Document management routes
@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all uploaded documents for the current user"""
    
    documents = db.query(DBDocument).filter(DBDocument.user_id == int(current_user_id)).all()
    
    document_list = [
        DocumentResponse(
            id=doc.id,
            doc_id=doc.doc_id,
            original_filename=doc.original_filename,
            file_size=doc.file_size,
            upload_date=doc.upload_date,
            status=doc.status
        )
        for doc in documents
    ]
    
    return DocumentListResponse(documents=document_list)

# @router.delete("/documents/{doc_id}")
# async def delete_document(
#     doc_id: str,
#     current_user_id: str = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Delete a document and its vector store"""
#     # Verify document belongs to user
#     db_document = (
#         db.query(Document)
#         .filter(Document.doc_id == doc_id, Document.user_id == int(current_user_id))
#         .first()
#     )
    
#     if not db_document:
#         raise HTTPException(status_code=404, detail="Document not found")
    
#     try:
#         # Delete from database
#         db.delete(db_document)
#         db.commit()
        
#         # Delete associated vector store
#         pdf_processor.delete_vectorstore(doc_id)
        
#         return {"message": f"Document {doc_id} deleted successfully"}
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

# Add the other routes as needed