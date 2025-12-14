import React, { useEffect, useState } from 'react'

export default function Public() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    const fetchPublic = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/public-data/')
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
        const json = await res.json()
        if (mounted) setData(json.message || JSON.stringify(json))
      } catch (err) {
        if (mounted) setError(err.message)
      }
    }
    fetchPublic()
    return () => { mounted = false }
  }, [])

  return (
    <div>
      <h1>Public Page</h1>
      {data && <p>Public API: {data}</p>}
      {!data && !error && <p>Loading public data...</p>}
      {error && <pre style={{ color: 'red' }}>{error}</pre>}
    </div>
  )
}
