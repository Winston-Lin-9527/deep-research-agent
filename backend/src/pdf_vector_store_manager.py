from typing import List, Optional
from pathlib import Path
import asyncio
import nest_asyncio
import shutil

from sqlalchemy.orm import Session
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma 

from src.database import DBDocument
import uuid
import os

class PDFVectorStoreMgr:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Create vector store from documents
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = Chroma(
            collection_name="document_collection",
            embedding_function=self.embeddings,
            persist_directory=".chroma_db"
        )

    async def process_pdf(
        self, 
        file_path: str, 
        original_filename: str, 
        user_id: int, 
        db: Session
    ) -> DBDocument:
        """
        Process a PDF file, extract text, create vector embeddings, 
        and store document metadata in PostgreSQL
        """
        # Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # Create document record in database (initially in processing state)
        db_document = DBDocument(
            doc_id=doc_id,
            user_id=user_id,
            filename=f"{doc_id}.pdf",
            original_filename=original_filename,
            file_size=os.path.getsize(file_path),
            status="processing"
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        try:
            # Load and split PDF content
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            docs = self.text_splitter.split_documents(pages)
            
            doc_uids = [str(uuid.uuid4()) for _ in docs]
            
            self.vector_store.add_documents(documents=docs, ids=doc_uids) # just add one
            
            # Update document status to processed
            db_document.status = "processed"
            db.commit()
            
            return db_document
            
        except Exception as e:
            # Update document status to failed
            db_document.status = "failed"
            db.commit()
            raise e
    
    async def similarity_search(
        self,
        # doc_id: str,
        query: str,
        k: int = 4
    ) -> List[Document]:
        """Search for similar documents in a specific vector store"""
        # todo: implement per-document vector stores to utilize doc_id or collection_id etc
        
        retrieved_docs = self.vector_store.similarity_search(query=query, k=k)
        serialized = "\n\n".join(
            (f"source: {doc.metadata}\n content: {doc.page_content}")
            for doc in retrieved_docs
        )
        
        return serialized, retrieved_docs
    
    # def delete_vectorstore(self, doc_id: str) -> bool:
    #     """Delete vectorstore for a document"""
    #     # Using asyncio.run to run the async method in a synchronous context
    #     # In a real application, this should also be async
    #     try:
    #         nest_asyncio.apply()
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #         loop.run_until_complete(self.vector_store_manager.delete_vector_store(doc_id))
    #         return True
    #     except Exception as e:
    #         # Alternative approach for sync context
    #         vectorstore_path = self.vector_store_manager.get_vectorstore_path(doc_id)
    #         if os.path.exists(vectorstore_path):
    #             shutil.rmtree(vectorstore_path)
    #             return True
    #         return False



# singleton instance
pdf_vector_store_mgr = PDFVectorStoreMgr()
