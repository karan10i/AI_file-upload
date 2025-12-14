import React from 'react'
import { ClerkProvider, SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Public from './pages/Public'
import { CLERK_PUBLISHABLE_KEY } from './clerk-setup'

function AppShell() {
  return (
    <div>
      <nav>
        <Link to="/">Dashboard</Link> | <Link to="/public">Public</Link>
      </nav>
      <hr />
      <Routes>
        <Route
          path="/"
          element={
            <>
              <SignedIn>
                <Dashboard />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          }
        />
        <Route path="/public" element={<Public />} />
      </Routes>
    </div>
  )
}

export default function App() {
  if (!CLERK_PUBLISHABLE_KEY || CLERK_PUBLISHABLE_KEY === 'YOUR_CLERK_PUBLISHABLE_KEY') {
    console.warn('Set VITE_CLERK_PUBLISHABLE_KEY in .env to use Clerk.');
  }

  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </ClerkProvider>
  )
}
