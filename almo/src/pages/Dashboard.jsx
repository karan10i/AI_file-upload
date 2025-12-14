import React, { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'

export default function Dashboard() {
  const { getToken, userId } = useAuth()
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    const fetchProtected = async () => {
      try {
        const token = await getToken()
        const res = await fetch('http://localhost:8000/api/protected-data/', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!res.ok) {
          const txt = await res.text()
          throw new Error(`${res.status} ${res.statusText} - ${txt}`)
        }

        const data = await res.json()
        if (mounted) setMessage(data.message || JSON.stringify(data))
      } catch (err) {
        if (mounted) setError(err.message)
      }
    }

    fetchProtected()
    return () => { mounted = false }
  }, [getToken])

  return (
    <div>
      <h1>Dashboard</h1>
      <p>userId: {userId}</p>
      {message && <p>Protected API: {message}</p>}
      {!message && !error && <p>Loading protected data...</p>}
      {error && <pre style={{ color: 'red' }}>{error}</pre>}
    </div>
  )
}
