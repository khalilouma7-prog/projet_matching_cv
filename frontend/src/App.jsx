import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Resultats from './pages/Results'
import Profile from './pages/Profile'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'

const PrivateRoute = ({ children }) => {
  const user = localStorage.getItem('user')
  return user ? children : <Navigate to="/login" />
}

function AppShell({ children }) {
  const location = useLocation()
  const isAuth = ['/login', '/register'].includes(location.pathname)
  const [page, setPage] = useState(location.pathname.replace('/', '') || 'dashboard')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const handleLogout = () => {
    localStorage.removeItem('user')
  }

  if (isAuth) return children

  return (
    <div className="app-layout">
      <Sidebar page={page} setPage={setPage} user={user} />
      <div className="app-main">
        <Topbar page={page} setPage={setPage} onLogout={handleLogout} />
        <div className="app-body">
          {children}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/results" element={<PrivateRoute><Resultats /></PrivateRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile user={user} /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}