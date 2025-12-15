"""
Celery tasks for asynchronous document processing.
"""
import os
import logging
import tempfile
import uuid
from typing import List

from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage

from .models import Document
from .utils import TextExtractor, TextChunker, EmbeddingGenerator
from .chroma_handler import ChromaHandler

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_uploaded_document(self, doc_id: str):
    """
    Main task to process an uploaded document.
    
    Args:
        doc_id: UUID string of the document to process
    """
    try:
        # Fetch document
        document = Document.objects.get(id=doc_id)
        logger.info(f"Starting processing for document {doc_id}: {document.title}")
        
        # Update status to processing
        document.status = 'processing'
        document.save()
        
        # Download file from storage to local temp file
        # Extract just the filename extension to avoid path issues with tempfile
        file_basename = os.path.basename(document.file.name)
        _, file_ext = os.path.splitext(file_basename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Copy file content
            with document.file.open('rb') as source:
                temp_file.write(source.read())
            temp_file_path = temp_file.name
        
        try:
            # Extract text
            logger.info(f"Extracting text from {document.title}")
            text_extractor = TextExtractor()
            extracted_text = text_extractor.extract_text(temp_file_path)
            
            if not extracted_text.strip():
                raise ValueError("No text extracted from document")
            
            # Chunk text
            logger.info(f"Chunking text for {document.title}")
            text_chunker = TextChunker()
            chunks = text_chunker.chunk_text(extracted_text)
            
            if not chunks:
                raise ValueError("No chunks created from extracted text")
            
            # Update status to embedding
            document.status = 'embedding'
            document.save()
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks from {document.title}")
            embedding_generator = EmbeddingGenerator()
            embeddings = embedding_generator.generate_embeddings(chunks)
            
            # Prepare data for ChromaDB
            chunk_ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_{i}"
                chunk_ids.append(chunk_id)
                metadatas.append({
                    'user_id': str(document.user.id),
                    'doc_id': str(document.id),
                    'chunk_index': i,
                    'document_title': document.title
                })
            
            # Store in ChromaDB
            logger.info(f"Storing embeddings in ChromaDB for {document.title}")
            chroma_handler = ChromaHandler()
            chroma_handler.add_documents(
                collection_name="documents",
                texts=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            # Update status to completed
            document.status = 'completed'
            document.error_message = ""
            document.save()
            
            logger.info(f"Successfully processed document {doc_id}: {document.title}")
            return f"Successfully processed {len(chunks)} chunks from {document.title}"
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Document.DoesNotExist:
        error_msg = f"Document with ID {doc_id} not found"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    except Exception as e:
        error_msg = f"Error processing document {doc_id}: {str(e)}"
        logger.error(error_msg)
        
        try:
            document = Document.objects.get(id=doc_id)
            document.status = 'failed'
            document.error_message = str(e)
            document.save()
        except Document.DoesNotExist:
            pass
        
        # Re-raise the exception for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task
def cleanup_failed_documents():
    """
    Periodic task to clean up old failed documents.
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=7)
    failed_docs = Document.objects.filter(
        status='failed',
        created_at__lt=cutoff_date
    )
    
    count = failed_docs.count()
    if count > 0:
        failed_docs.delete()
        logger.info(f"Cleaned up {count} old failed documents")
    
    return f"Cleaned up {count} failed documents"