import React from 'react';
import { SignUp } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

export default function SignUpPage() {
  const navigate = useNavigate();

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-content">
          <h1>Create Account</h1>
          <p>Sign up to start chatting</p>
          <SignUp
            path="/sign-up"
            routing="path"
            signInUrl="/sign-in"
            afterSignUpUrl="/dashboard"
          />
          <div className="auth-footer">
            <p>Already have an account? <button onClick={() => navigate('/sign-in')} className="link-btn">Sign in</button></p>
          </div>
        </div>
      </div>
    </div>
  );
}
