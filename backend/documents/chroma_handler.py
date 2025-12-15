"""
ChromaDB integration for vector storage and retrieval.
"""
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from django.conf import settings

logger = logging.getLogger(__name__)


class ChromaHandler:
    """
    Handles ChromaDB operations for document embeddings.
    """
    
    def __init__(self):
        """
        Initialize ChromaDB client.
        """
        try:
            # Use HTTP client for Docker setup
            host = getattr(settings, 'CHROMADB_HOST', 'chroma')
            port = int(getattr(settings, 'CHROMADB_PORT', '8000'))
            
            self.client = chromadb.HttpClient(
                host=host,
                port=port
            )
            logger.info(f"ChromaDB client initialized successfully at {host}:{port}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    
    def get_or_create_collection(self, collection_name: str = "documents"):
        """
        Get or create a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection instance
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document embeddings with user isolation"}
            )
            logger.info(f"Collection '{collection_name}' ready")
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection '{collection_name}': {str(e)}")
            raise
    
    def add_documents(
        self, 
        collection_name: str,
        texts: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add document chunks with embeddings to ChromaDB.
        
        Args:
            collection_name: Name of the collection
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for each chunk
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    def search_documents(
        self, 
        collection_name: str,
        query_embedding: List[float], 
        user_id: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search for similar documents by user.
        
        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            user_id: User ID for filtering results
            n_results: Number of results to return
            
        Returns:
            Search results dictionary
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"user_id": user_id}
            )
            
            logger.info(f"Search returned {len(results['documents'][0])} results for user {user_id}")
            return results
        except Exception as e:
            logger.error(f"Error searching documents in ChromaDB: {str(e)}")
            raise
    
    def delete_user_documents(self, collection_name: str, user_id: str, doc_id: str = None):
        """
        Delete documents for a user or specific document.
        
        Args:
            collection_name: Name of the collection
            user_id: User ID
            doc_id: Optional specific document ID to delete
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            if doc_id:
                # Delete specific document chunks
                where_filter = {"user_id": user_id, "doc_id": doc_id}
            else:
                # Delete all user documents
                where_filter = {"user_id": user_id}
            
            # ChromaDB delete by metadata filter
            collection.delete(where=where_filter)
            
            logger.info(f"Deleted documents for user {user_id}, doc_id: {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting documents from ChromaDB: {str(e)}")
            raise