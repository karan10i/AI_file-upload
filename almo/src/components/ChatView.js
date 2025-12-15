import React, { useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function ChatView({ chat, onSendMessage, isLoading }) {
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadErrors, setUploadErrors] = useState({});
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [chat?.messages]);

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
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

  const validateFile = (file) => {
    const allowedTypes = ['.pdf', '.docx', '.txt'];
    const maxSize = 50 * 1024 * 1024; // 50MB
    
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(extension)) {
      return `Unsupported file type "${extension}". Allowed types: ${allowedTypes.join(', ')}`;
    }
    
    if (file.size > maxSize) {
      return `File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum allowed size (50MB)`;
    }
    
    return null;
  };

  const uploadToServer = async (file) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name.split('.')[0]); // Use filename without extension as title

    try {
      const response = await fetch('http://localhost:8000/api/documents/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.file?.[0] || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(error.message || 'Network error occurred');
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadErrors({});
    
    // Process files one by one
    for (const file of files) {
      const fileId = `${file.name}_${Date.now()}`;
      
      try {
        // Validate file
        const validationError = validateFile(file);
        if (validationError) {
          setUploadErrors(prev => ({ ...prev, [fileId]: validationError }));
          onSendMessage(`❌ Upload failed: ${file.name} - ${validationError}`);
          continue;
        }

        // Set uploading progress
        setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));
        onSendMessage(`📤 Uploading: ${file.name}...`);

        // Upload to server
        const document = await uploadToServer(file);
        
        // Update local state
        setUploadedFiles(prev => [...prev, {
          id: document.id,
          name: file.name,
          size: file.size,
          type: file.type,
          status: document.status,
          uploadedAt: new Date()
        }]);

        // Clear progress
        setUploadProgress(prev => {
          const { [fileId]: _, ...rest } = prev;
          return rest;
        });

        // Notify success and start polling for status
        onSendMessage(`✅ Uploaded: ${file.name} (Processing...)`);
        startPollingDocumentStatus(document.id, file.name);

      } catch (error) {
        setUploadErrors(prev => ({ ...prev, [fileId]: error.message }));
        onSendMessage(`❌ Upload failed: ${file.name} - ${error.message}`);
        
        // Clear progress on error
        setUploadProgress(prev => {
          const { [fileId]: _, ...rest } = prev;
          return rest;
        });
      }
    }
    
    setIsUploading(false);
    // Clear the file input
    e.target.value = '';
  };

  const startPollingDocumentStatus = async (documentId, fileName) => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/documents/${documentId}/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const document = await response.json();
          
          // Update local state
          setUploadedFiles(prev => 
            prev.map(file => 
              file.id === documentId 
                ? { ...file, status: document.status, error_message: document.error_message }
                : file
            )
          );

          if (document.status === 'completed') {
            onSendMessage(`🎉 Document processed successfully: ${fileName}`);
          } else if (document.status === 'failed') {
            onSendMessage(`❌ Processing failed: ${fileName} - ${document.error_message}`);
          } else if (document.status === 'processing' || document.status === 'embedding') {
            // Continue polling
            setTimeout(pollStatus, 3000);
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
      }
    };

    // Start polling after a short delay
    setTimeout(pollStatus, 2000);
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
              <div className="message-sender">{msg.sender === 'Bot' ? 'AI Assistant' : msg.sender}</div>
              <div className="message-text" style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message bot">
            <div className="message-sender">AI Assistant</div>
            <div className="typing-indicator">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          multiple
          accept=".pdf,.docx,.txt"
        />
        <button 
          onClick={handleFileButtonClick} 
          className="file-upload-btn" 
          title="Upload documents (PDF, DOCX, TXT)"
          disabled={isUploading || isLoading}
        >
          {isUploading ? '⏳' : '📎'}
        </button>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isLoading ? "Waiting for response..." : "Type your message... (Shift+Enter for new line)"}
          rows="3"
          disabled={isLoading}
        />
        <button onClick={handleSend} className="send-btn" disabled={isLoading || !inputValue.trim()}>
          {isLoading ? '⏳' : 'Send ➤'}
        </button>
        
        {/* Upload status indicator */}
        {isUploading && (
          <div className="upload-status">
            Uploading documents...
          </div>
        )}
      </div>
    </div>
  );
}
