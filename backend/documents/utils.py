"""
Text processing utilities for document handling.
"""
import os
import logging
from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Handles text extraction from various document formats.
    """
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from PDF, DOCX, or TXT files.
        
        Args:
            file_path: Path to the file to extract text from
            
        Returns:
            Extracted text as string
            
        Raises:
            ValueError: If file format is not supported
            Exception: If extraction fails
        """
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.pdf':
                return TextExtractor._extract_from_pdf(file_path)
            elif file_extension == '.docx':
                return TextExtractor._extract_from_docx(file_path)
            elif file_extension == '.txt':
                return TextExtractor._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = DocxDocument(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text).strip()
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()


class TextChunker:
    """
    Handles intelligent text chunking using LangChain's RecursiveCharacterTextSplitter.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into intelligent chunks respecting paragraph boundaries.
        
        Args:
            text: Text to be chunked
            
        Returns:
            List of text chunks
        """
        if not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]


class EmbeddingGenerator:
    """
    Generates embeddings using local HuggingFace models.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.embeddings_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.
        
        Args:
            texts: List of text chunks
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings_model.embed_documents(texts)


def get_embedding_function():
    """
    Get the default embedding function for use in ChromaDB.
    
    Returns:
        HuggingFaceEmbeddings instance
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )