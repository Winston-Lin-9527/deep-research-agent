from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, ForeignKey, Boolean, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost:5432/postgres")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# define a table & schema
class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to documents
    documents = relationship("Document", back_populates="owner")

class DBDocument(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True, nullable=False)  # UUID for document
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)  # Original filename
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    content_type = Column(String, default="application/pdf")  # MIME type
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processing")  # processing, processed, failed
    
    # Relationship to user
    owner = relationship("User", back_populates="documents")

# Create tables
def create_tables():
    inspector = inspect(engine)
    tables_exist = inspector.has_table("users") and inspector.has_table("documents")
    if not tables_exist:
        Base.metadata.create_all(bind=engine)
    else:
        print("Table(s) already exist. Skipping creation.")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()