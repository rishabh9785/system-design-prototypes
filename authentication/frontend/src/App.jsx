import { useState, useEffect } from 'react'
import Signup from './pages/Signup.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [page, setPage] = useState(token ? 'dashboard' : 'login')

  useEffect(() => {
    setPage(token ? 'dashboard' : 'login')
  }, [])

  function handleLogin(newToken) {
    localStorage.setItem('token', newToken)
    setToken(newToken)
    setPage('dashboard')
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken(null)
    setPage('login')
  }

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 400, margin: '40px auto' }}>
      <h1>JWT Auth Demo</h1>
      {page !== 'dashboard' && (
        <div style={{ marginBottom: 16 }}>
          <button onClick={() => setPage('login')}>Login</button>{' '}
          <button onClick={() => setPage('signup')}>Signup</button>
        </div>
      )}
      {page === 'signup' && <Signup onDone={() => setPage('login')} />}
      {page === 'login' && <Login onLogin={handleLogin} />}
      {page === 'dashboard' && <Dashboard token={token} onLogout={handleLogout} />}
    </div>
  )
}
