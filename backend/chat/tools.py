"""
LangChain tools for the AI Agent.
These tools allow the AI to search documents, create tasks, and list tasks.
"""
import logging
from typing import Optional
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


def get_document_search_tool(user_id: str):
    """
    Factory function to create a document search tool bound to a specific user.
    """
    from documents.chroma_handler import ChromaHandler
    from documents.utils import EmbeddingGenerator
    
    @tool
    def search_documents(query: str) -> str:
        """
        Search for relevant information in the user's uploaded documents.
        Use this tool when the user asks questions about their documents or files.
        
        Args:
            query: The search query to find relevant document chunks.
            
        Returns:
            Relevant text chunks from the user's documents.
        """
        try:
            logger.info(f"Searching documents for user {user_id} with query: {query}")
            
            # Generate embedding for the query
            embedding_generator = EmbeddingGenerator()
            query_embedding = embedding_generator.generate_embeddings([query])[0]
            
            # Search ChromaDB
            chroma_handler = ChromaHandler()
            results = chroma_handler.search_documents(
                collection_name="documents",
                query_embedding=query_embedding,
                user_id=user_id,
                n_results=5
            )
            
            if not results or not results.get('documents') or not results['documents'][0]:
                return "No relevant information found in your uploaded documents."
            
            # Format results
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            
            formatted_results = []
            for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
                doc_title = meta.get('document_title', 'Unknown Document')
                formatted_results.append(f"[Source: {doc_title}]\n{doc}")
            
            return "\n\n---\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return f"Error searching documents: {str(e)}"
    
    return search_documents


def get_create_task_tool(user):
    """
    Factory function to create a task creation tool bound to a specific user.
    """
    from tasks.models import Task
    
    @tool
    def create_task(title: str, priority: str = "medium", description: str = "") -> str:
        """
        Create a new task for the user. Use this when the user asks to create a task,
        add a reminder, or set up something to do.
        
        Args:
            title: The title/name of the task.
            priority: Priority level - must be one of: 'low', 'medium', 'high'. Default is 'medium'.
            description: Optional description for the task.
            
        Returns:
            Confirmation message with task details.
        """
        try:
            logger.info(f"Creating task for user {user.id}: {title}")
            
            # Validate priority
            valid_priorities = ['low', 'medium', 'high']
            if priority.lower() not in valid_priorities:
                priority = 'medium'
            
            task = Task.objects.create(
                title=title,
                description=description,
                priority=priority.lower(),
                status='todo',
                created_by=user,
                created_by_ai=True
            )
            
            return f"✅ Task created successfully!\n- Title: {task.title}\n- Priority: {task.priority}\n- Status: {task.status}\n- ID: {task.id}"
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return f"Error creating task: {str(e)}"
    
    return create_task


def get_list_tasks_tool(user):
    """
    Factory function to create a task listing tool bound to a specific user.
    """
    from tasks.models import Task
    
    @tool
    def list_tasks(status_filter: Optional[str] = None) -> str:
        """
        List the user's tasks. Use this when the user asks to see their tasks,
        to-dos, or what they have to do.
        
        Args:
            status_filter: Optional filter - 'todo', 'in_progress', 'done', or 'all'. Default shows active tasks.
            
        Returns:
            List of tasks with their details.
        """
        try:
            logger.info(f"Listing tasks for user {user.id}")
            
            queryset = Task.objects.filter(created_by=user)
            
            if status_filter and status_filter != 'all':
                if status_filter in ['todo', 'in_progress', 'done']:
                    queryset = queryset.filter(status=status_filter)
            else:
                # By default, show only active (non-done) tasks
                queryset = queryset.exclude(status='done')
            
            tasks = queryset.order_by('-priority', '-created_at')[:10]
            
            if not tasks:
                return "You don't have any active tasks."
            
            result = "📋 Your Tasks:\n\n"
            for task in tasks:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(task.priority, '⚪')
                status_emoji = {'todo': '⬜', 'in_progress': '🔄', 'done': '✅'}.get(task.status, '⬜')
                ai_badge = ' [AI]' if task.created_by_ai else ''
                
                result += f"{status_emoji} {priority_emoji} {task.title}{ai_badge}\n"
                if task.description:
                    result += f"   {task.description[:50]}...\n"
                result += "\n"
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return f"Error listing tasks: {str(e)}"
    
    return list_tasks


def get_list_documents_tool(user):
    """
    Factory function to create a document listing tool bound to a specific user.
    """
    from documents.models import Document
    
    @tool
    def list_documents() -> str:
        """
        List all documents uploaded by the user. Use this when the user asks
        what documents or files they have uploaded.
        
        Returns:
            List of uploaded documents with their status.
        """
        try:
            logger.info(f"Listing documents for user {user.id}")
            
            documents = Document.objects.filter(user=user).order_by('-created_at')[:10]
            
            if not documents:
                return "You haven't uploaded any documents yet."
            
            result = "📁 Your Documents:\n\n"
            for doc in documents:
                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄',
                    'embedding': '🧠',
                    'completed': '✅',
                    'failed': '❌'
                }.get(doc.status, '❓')
                
                result += f"{status_emoji} {doc.title} ({doc.status})\n"
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return f"Error listing documents: {str(e)}"
    
    return list_documents
