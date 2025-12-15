import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar({ chats, selectedChatId, onSelectChat, onNewChat }) {
  const [documents, setDocuments] = useState([]);
  const [showKnowledgeHub, setShowKnowledgeHub] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/api/documents/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const docs = await response.json();
        setDocuments(docs);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'processing': return '🔄';
      case 'embedding': return '🧠';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '📄';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#ffa500';
      case 'processing': return '#2196f3';
      case 'embedding': return '#9c27b0';
      case 'completed': return '#4caf50';
      case 'failed': return '#f44336';
      default: return '#757575';
    }
  };

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

      {/* Knowledge Hub Section */}
      <div className="knowledge-hub-section">
        <div 
          className="section-header" 
          onClick={() => setShowKnowledgeHub(!showKnowledgeHub)}
          style={{ cursor: 'pointer' }}
        >
          <h3>📚 Knowledge Hub {showKnowledgeHub ? '▾' : '▸'}</h3>
          <span className="document-count">({documents.length})</span>
        </div>
        
        {showKnowledgeHub && (
          <div className="documents-list">
            {documents.length === 0 ? (
              <div className="empty-documents">
                <p>No documents uploaded yet</p>
                <small>Upload PDFs, DOCX, or TXT files via chat</small>
              </div>
            ) : (
              documents.map(doc => (
                <div key={doc.id} className="document-item">
                  <span 
                    className="document-status" 
                    style={{ color: getStatusColor(doc.status) }}
                    title={doc.status}
                  >
                    {getStatusIcon(doc.status)}
                  </span>
                  <div className="document-info">
                    <div className="document-title" title={doc.title}>
                      {doc.title.length > 20 ? `${doc.title.substring(0, 20)}...` : doc.title}
                    </div>
                    <div className="document-date">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button 
                    className="document-menu"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Could add document actions here
                    }}
                  >
                    ⋯
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-stats">
          <p>{chats.length} chats • {documents.filter(d => d.status === 'completed').length} docs ready</p>
        </div>
      </div>
    </aside>
  );
}
