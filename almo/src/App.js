import React from 'react';
import { ClerkProvider, SignedIn, useAuth } from '@clerk/clerk-react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SignInPage from './pages/SignInPage';
import SignUpPage from './pages/SignUpPage';
import DashboardLayout from './pages/DashboardLayout';
import ProfilePage from './pages/ProfilePage';
import './App.css';

const clerkPublishableKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

function AppRoutes() {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) return <div className="loading">Loading...</div>;

  return (
    <Routes>
      <Route path="/sign-in/*" element={<SignInPage />} />
      <Route path="/sign-up/*" element={<SignUpPage />} />
      <Route
        path="/dashboard/*"
        element={
          <SignedIn>
            <DashboardLayout />
          </SignedIn>
        }
      />
      <Route
        path="/profile"
        element={
          <SignedIn>
            <ProfilePage />
          </SignedIn>
        }
      />
      <Route path="/" element={isSignedIn ? <Navigate to="/dashboard" /> : <Navigate to="/sign-in" />} />
    </Routes>
  );
}

function App() {
  if (!clerkPublishableKey) {
    throw new Error('REACT_APP_CLERK_PUBLISHABLE_KEY is missing');
  }

  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ClerkProvider>
  );
}

export default App;
