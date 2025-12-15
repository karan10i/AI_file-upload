import React, { useState } from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import ChatView from '../components/ChatView';

export default function DashboardLayout() {
  const [chats, setChats] = useState([
    { id: 1, name: 'AI Assistant', messages: [{ id: 1, sender: 'Bot', text: 'Welcome! I can help you search your documents, create tasks, and answer questions. How can I assist you today?' }] },
  ]);
  const [selectedChatId, setSelectedChatId] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const selectedChat = chats.find(c => c.id === selectedChatId);

  const handleSendMessage = async (text) => {
    // Add user message immediately
    const userMessageId = Date.now();
    setChats(chats.map(chat => {
      if (chat.id === selectedChatId) {
        return {
          ...chat,
          messages: [
            ...chat.messages,
            { id: userMessageId, sender: 'You', text }
          ]
        };
      }
      return chat;
    }));

    // Don't call AI for system messages (upload notifications)
    if (text.startsWith('📤') || text.startsWith('✅') || text.startsWith('❌') || text.startsWith('🎉')) {
      return;
    }

    // Call the AI chat API
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.detail || 'Failed to get response');
      }

      const data = await response.json();
      
      // Add AI response to chat
      setChats(prevChats => prevChats.map(chat => {
        if (chat.id === selectedChatId) {
          return {
            ...chat,
            messages: [
              ...chat.messages,
              { id: Date.now(), sender: 'Bot', text: data.response }
            ]
          };
        }
        return chat;
      }));

    } catch (error) {
      console.error('Chat error:', error);
      // Add error message to chat
      setChats(prevChats => prevChats.map(chat => {
        if (chat.id === selectedChatId) {
          return {
            ...chat,
            messages: [
              ...chat.messages,
              { id: Date.now(), sender: 'Bot', text: `❌ Error: ${error.message}` }
            ]
          };
        }
        return chat;
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    const newId = Math.max(...chats.map(c => c.id), 0) + 1;
    const newChat = { 
      id: newId, 
      name: `Chat ${newId}`, 
      messages: [{ id: 1, sender: 'Bot', text: 'How can I help you today?' }] 
    };
    setChats([...chats, newChat]);
    setSelectedChatId(newId);
  };

  return (
    <div className="dashboard-layout">
      <Header />
      <div className="dashboard-content">
        <Sidebar
          chats={chats}
          selectedChatId={selectedChatId}
          onSelectChat={setSelectedChatId}
          onNewChat={handleNewChat}
        />
        <ChatView
          chat={selectedChat}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
