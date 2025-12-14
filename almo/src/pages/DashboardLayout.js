import React, { useState } from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import ChatView from '../components/ChatView';

export default function DashboardLayout() {
  const [chats, setChats] = useState([
    { id: 1, name: 'General Chat', messages: [{ id: 1, sender: 'Bot', text: 'Welcome to Almo!' }] },
    { id: 2, name: 'Project Discussion', messages: [{ id: 1, sender: 'You', text: 'Hey, how is the project?' }] },
  ]);
  const [selectedChatId, setSelectedChatId] = useState(1);

  const selectedChat = chats.find(c => c.id === selectedChatId);

  const handleSendMessage = (text) => {
    setChats(chats.map(chat => {
      if (chat.id === selectedChatId) {
        return {
          ...chat,
          messages: [
            ...chat.messages,
            { id: chat.messages.length + 1, sender: 'You', text }
          ]
        };
      }
      return chat;
    }));
  };

  const handleNewChat = () => {
    const newId = Math.max(...chats.map(c => c.id), 0) + 1;
    const newChat = { id: newId, name: `Chat ${newId}`, messages: [] };
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
        />
      </div>
    </div>
  );
}
