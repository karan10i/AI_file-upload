import React from 'react';

export default function Sidebar({ chats, selectedChatId, onSelectChat, onNewChat }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          ✏️ New Chat
        </button>
      </div>

      <div className="chat-list">
        {chats.map(chat => (
          <div
            key={chat.id}
            className={`chat-item ${selectedChatId === chat.id ? 'active' : ''}`}
            onClick={() => onSelectChat(chat.id)}
          >
            <div className="chat-icon">💬</div>
            <div className="chat-name">{chat.name}</div>
            <button className="chat-menu">⋯</button>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-stats">
          <p>{chats.length} chats</p>
        </div>
      </div>
    </aside>
  );
}
