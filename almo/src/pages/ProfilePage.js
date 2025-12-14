import React from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

export default function ProfilePage() {
  const { user } = useUser();
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/sign-in';
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">← Back to Chat</button>
        <h1>Profile</h1>
      </div>

      <div className="profile-card">
        <div className="profile-avatar">
          {user?.profileImageUrl ? (
            <img src={user.profileImageUrl} alt="Profile" />
          ) : (
            <div className="avatar-placeholder">
              {user?.firstName?.charAt(0)}{user?.lastName?.charAt(0)}
            </div>
          )}
        </div>

        <div className="profile-info">
          <div className="info-row">
            <label>First Name</label>
            <p>{user?.firstName || 'Not set'}</p>
          </div>
          <div className="info-row">
            <label>Last Name</label>
            <p>{user?.lastName || 'Not set'}</p>
          </div>
          <div className="info-row">
            <label>Email</label>
            <p>{user?.primaryEmailAddress?.emailAddress}</p>
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
