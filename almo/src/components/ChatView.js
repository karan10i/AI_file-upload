import React, { useState, useRef } from 'react';

export default function ChatView({ chat, onSendMessage }) {
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      // Save files locally using browser's File API
      const fileDetails = files.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      }));
      setUploadedFiles(prev => [...prev, ...fileDetails]);
      
      // Send message about uploaded file
      const fileNames = files.map(f => f.name).join(', ');
      onSendMessage(`📎 Uploaded: ${fileNames}`);
      
      // Store file reference (in production, this would upload to server)
      console.log('Files ready for upload:', files);
    }
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  if (!chat) {
    return (
      <div className="chat-view empty">
        <div className="empty-state">
          <h2>No chat selected</h2>
          <p>Select a chat from the sidebar or create a new one</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-view">
      <div className="chat-header">
        <h2>{chat.name}</h2>
      </div>

      <div className="messages-container">
        {chat.messages.length === 0 ? (
          <div className="empty-messages">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          chat.messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender === 'You' ? 'user' : 'bot'}`}>
              <div className="message-sender">{msg.sender}</div>
              <div className="message-text">{msg.text}</div>
            </div>
          ))
        )}
      </div>

      <div className="chat-input-area">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          multiple
        />
        <button onClick={handleFileButtonClick} className="file-upload-btn" title="Upload files">
          📎
        </button>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Shift+Enter for new line)"
          rows="3"
        />
        <button onClick={handleSend} className="send-btn">
          Send ➤
        </button>
      </div>
    </div>
  );
}
