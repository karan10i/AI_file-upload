import React, { useState } from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const { user } = useUser();
  const { signOut } = useClerk();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/sign-in';
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo">💬 Almo</h1>
        </div>
        <div className="header-right">
          <div className="profile-menu">
            <button
              className="profile-btn"
              onClick={() => setShowMenu(!showMenu)}
              title={user?.fullName}
            >
              {user?.profileImageUrl ? (
                <img src={user.profileImageUrl} alt="Profile" />
              ) : (
                <div className="avatar-mini">
                  {user?.firstName?.charAt(0)}{user?.lastName?.charAt(0)}
                </div>
              )}
            </button>
            {showMenu && (
              <div className="profile-dropdown">
                <div className="dropdown-header">
                  <strong>{user?.fullName}</strong>
                </div>
                <hr />
                <button onClick={() => navigate('/profile')}>Profile</button>
                <button onClick={() => navigate('/settings')}>Settings</button>
                <hr />
                <button className="logout-btn" onClick={handleSignOut}>Sign Out</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
