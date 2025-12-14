import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  const handleSignOut = () => {
    logout();
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
              title={user?.first_name + ' ' + user?.last_name}
            >
              <div className="avatar-mini">
                {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
              </div>
            </button>
            {showMenu && (
              <div className="profile-dropdown">
                <div className="dropdown-header">
                  <strong>{user?.first_name} {user?.last_name}</strong>
                  <small>{user?.email}</small>
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
