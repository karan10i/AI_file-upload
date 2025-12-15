"""
AI Agent implementation using LangChain and Groq.
This is the 'brain' of the AI Workspace that can search documents,
create tasks, and maintain conversation context.
"""
import os
import logging
from typing import List, Dict, Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .tools import (
    get_document_search_tool,
    get_create_task_tool,
    get_list_tasks_tool,
    get_list_documents_tool
)

logger = logging.getLogger(__name__)

# System prompt for the AI agent
SYSTEM_PROMPT = """You are an intelligent AI assistant for an AI Workspace application. 
You help users manage their documents and tasks efficiently.

Your capabilities:
1. **Document Search**: You can search through the user's uploaded documents to answer questions.
   Use the search_documents tool when users ask about content in their files.

2. **Task Management**: You can create tasks and list the user's tasks.
   Use create_task when users want to add a task, reminder, or to-do item.
   Use list_tasks when users want to see their tasks.

3. **Document Listing**: You can show users what documents they have uploaded.
   Use list_documents when users ask about their uploaded files.

Important guidelines:
- When answering questions about documents, ALWAYS use the search_documents tool first.
- If the search returns no relevant information, clearly state: "This information is not available in your uploaded documents."
- Be helpful, concise, and accurate.
- When creating tasks, confirm the details with the user.
- Format your responses clearly using markdown when appropriate.

Remember: You can only access documents that the user has uploaded. You cannot browse the internet or access external sources."""


class AIAgent:
    """
    AI Agent that uses Groq's LLM with tools for document search and task management.
    """
    
    def __init__(self, user):
        """
        Initialize the AI agent for a specific user.
        
        Args:
            user: Django User object
        """
        self.user = user
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.tools_dict = {tool.name: tool for tool in self.tools}
        self.agent = self._create_agent()
    
    def _initialize_llm(self) -> ChatGroq:
        """
        Initialize the Groq LLM.
        """
        groq_api_key = os.environ.get('GROQ_API_KEY')
        
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        return ChatGroq(
            model="llama-3.1-8b-instant",  # Using smaller model that's more stable with tools
            api_key=groq_api_key,
            temperature=0.3,  # Lower temperature for more consistent tool calls
            max_tokens=2048,
        )
    
    def _get_tools(self) -> List:
        """
        Get the tools available to the agent, bound to the current user.
        """
        return [
            get_document_search_tool(str(self.user.id)),
            get_create_task_tool(self.user),
            get_list_tasks_tool(self.user),
            get_list_documents_tool(self.user),
        ]
    
    def _create_agent(self):
        """
        Create the agent with tools bound to the LLM.
        """
        # Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(self.tools)
        return llm_with_tools
    
    def _format_chat_history(self, chat_history: List[Dict]) -> List:
        """
        Convert chat history from database format to LangChain messages.
        
        Args:
            chat_history: List of dicts with 'role' and 'content' keys
            
        Returns:
            List of LangChain message objects
        """
        messages = []
        for msg in chat_history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
        return messages
    
    def _execute_tool_calls(self, tool_calls: List) -> List[ToolMessage]:
        """
        Execute tool calls and return ToolMessage objects.
        """
        tool_messages = []
        
        for tool_call in tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call.get('id', tool_name)
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            
            # Find and execute the matching tool
            if tool_name in self.tools_dict:
                try:
                    result = self.tools_dict[tool_name].invoke(tool_args)
                    tool_messages.append(ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id
                    ))
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    tool_messages.append(ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_id
                    ))
            else:
                tool_messages.append(ToolMessage(
                    content=f"Unknown tool: {tool_name}",
                    tool_call_id=tool_id
                ))
        
        return tool_messages
    
    def chat_sync(self, user_message: str, chat_history: List[Dict] = None) -> str:
        """
        Synchronous version of chat for non-async contexts.
        
        Args:
            user_message: The user's input message
            chat_history: Previous messages in the conversation
            
        Returns:
            The AI assistant's response
        """
        if chat_history is None:
            chat_history = []
        
        try:
            # Build messages list
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            messages.extend(self._format_chat_history(chat_history))
            messages.append(HumanMessage(content=user_message))
            
            # Get initial response from LLM
            response = self.agent.invoke(messages)
            
            # Check if the LLM wants to use tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Execute tools
                tool_messages = self._execute_tool_calls(response.tool_calls)
                
                # Add the AI response and tool results
                messages.append(response)
                messages.extend(tool_messages)
                
                # Get final response (without tools to avoid loops)
                final_response = self.llm.invoke(messages)
                return final_response.content
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error in AI chat: {str(e)}")
            raise
    
    async def chat(self, user_message: str, chat_history: List[Dict] = None) -> str:
        """
        Async version of chat.
        """
        # For now, just use the sync version
        return self.chat_sync(user_message, chat_history)
