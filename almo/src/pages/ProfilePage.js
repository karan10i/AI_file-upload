import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = () => {
    logout();
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">← Back to Chat</button>
        <h1>Profile</h1>
      </div>

      <div className="profile-card">
        <div className="profile-avatar">
          <div className="avatar-placeholder">
            {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
          </div>
        </div>

        <div className="profile-info">
          <div className="info-row">
            <label>First Name</label>
            <p>{user?.first_name || 'Not set'}</p>
          </div>
          <div className="info-row">
            <label>Last Name</label>
            <p>{user?.last_name || 'Not set'}</p>
          </div>
          <div className="info-row">
            <label>Email</label>
            <p>{user?.email}</p>
          </div>
          <div className="info-row">
            <label>Username</label>
            <p>{user?.username}</p>
          </div>
          <div className="info-row">
            <label>Workspace</label>
            <p>{user?.workspace_name || 'Default Workspace'}</p>
          </div>
          <div className="info-row">
            <label>User ID</label>
            <p className="user-id">{user?.id}</p>
          </div>
        </div>

        <div className="profile-actions">
          <button className="btn-secondary">Edit Profile</button>
          <button className="btn-danger" onClick={handleSignOut}>Sign Out</button>
        </div>
      </div>
    </div>
  );
}
