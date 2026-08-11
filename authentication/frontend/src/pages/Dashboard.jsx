import { useState, useEffect } from 'react'
import { getMe } from '../api.js'

export default function Dashboard({ token, onLogout }) {
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getMe(token)
      .then(setUser)
      .catch((err) => setError(err.message))
  }, [token])

  return (
    <div>
      <h2>Dashboard</h2>
      {error && (
        <div>
          <p style={{ color: 'red' }}>{error}</p>
          <button onClick={onLogout}>Back to login</button>
        </div>
      )}
      {user && (
        <div>
          <p>
            Logged in as <strong>{user.email}</strong>
          </p>
          <p>User ID: {user.user_id}</p>
          <button onClick={onLogout}>Logout</button>
        </div>
      )}
    </div>
  )
}
