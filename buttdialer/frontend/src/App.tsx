import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Calls from './pages/Calls'
import Teams from './pages/Teams'
import Contacts from './pages/Contacts'
import Compliance from './pages/Compliance'
import Settings from './pages/Settings'

function App() {
  const { user, isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/calls" element={<Calls />} />
        <Route path="/teams" element={<Teams />} />
        <Route path="/contacts" element={<Contacts />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App