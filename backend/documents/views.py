"""
API views for document management.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document
from .serializers import DocumentSerializer, DocumentListSerializer
from .tasks import process_uploaded_document
from .chroma_handler import ChromaHandler

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for document CRUD operations with user isolation.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter documents by current user."""
        return Document.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use simplified serializer for list view."""
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer
    
    def perform_create(self, serializer):
        """Save document and trigger processing task."""
        document = serializer.save()
        
        # Trigger async processing
        try:
            task = process_uploaded_document.delay(str(document.id))
            logger.info(f"Started processing task {task.id} for document {document.id}")
        except Exception as e:
            logger.error(f"Error starting processing task for document {document.id}: {str(e)}")
            # Update document status to failed
            document.status = 'failed'
            document.error_message = f"Failed to start processing: {str(e)}"
            document.save()
    
    def destroy(self, request, *args, **kwargs):
        """Delete document and associated embeddings."""
        document = self.get_object()
        
        # Delete from ChromaDB if processing was completed
        if document.status == 'completed':
            try:
                chroma_handler = ChromaHandler()
                chroma_handler.delete_user_documents(
                    collection_name="documents",
                    user_id=str(request.user.id),
                    doc_id=str(document.id)
                )
                logger.info(f"Deleted embeddings for document {document.id}")
            except Exception as e:
                logger.error(f"Error deleting embeddings for document {document.id}: {str(e)}")
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """
        Reprocess a document (reset status and trigger processing again).
        """
        document = self.get_object()
        
        # Only allow reprocessing if not currently processing
        if document.status == 'processing':
            return Response(
                {'error': 'Document is currently being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status and clear error message
        document.status = 'pending'
        document.error_message = ''
        document.save()
        
        # Trigger processing
        try:
            task = process_uploaded_document.delay(str(document.id))
            logger.info(f"Started reprocessing task {task.id} for document {document.id}")
            
            return Response(
                {'message': 'Document reprocessing started', 'task_id': task.id},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error starting reprocessing task for document {document.id}: {str(e)}")
            
            # Update status to failed
            document.status = 'failed'
            document.error_message = f"Failed to start reprocessing: {str(e)}"
            document.save()
            
            return Response(
                {'error': 'Failed to start reprocessing'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
