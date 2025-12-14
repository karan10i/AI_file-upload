import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

export default function SignInPage() {
  const navigate = useNavigate();

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-content">
          <h1>Welcome Back</h1>
          <p>Sign in to continue to your chats</p>
          <SignIn
            path="/sign-in"
            routing="path"
            signUpUrl="/sign-up"
            afterSignInUrl="/dashboard"
          />
          <div className="auth-footer">
            <p>Don't have an account? <button onClick={() => navigate('/sign-up')} className="link-btn">Sign up</button></p>
          </div>
        </div>
      </div>
    </div>
  );
}
