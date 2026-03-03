import { Routes, Route, Navigate } from 'react-router-dom'
import { useThemeStore } from './store/themeStore'
import Layout from './components/Layout'
import AgentChat from './pages/AgentChat'
import AgentList from './pages/AgentList'
import Orchestration from './pages/Orchestration'
import Dashboard from './pages/Dashboard'
import LandingPage from './pages/LandingPage'
import AgentDetailPage from './pages/AgentDetailPage'
import AllAgentsPage from './pages/AllAgentsPage'
import { ScenarioSelector, SimulationWorkspace } from './pages/simulation'

function App() {
  const { isDark } = useThemeStore()

  return (
    <div className={isDark ? 'dark' : ''}>
      <Routes>
        {/* Public Landing Page - No Layout */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/agents" element={<AllAgentsPage />} />
        <Route path="/agents/:agentId" element={<AgentDetailPage />} />
        
        {/* Simulation/Training Routes */}
        <Route path="/in-flow-simulation" element={<ScenarioSelector />} />
        <Route path="/in-flow-simulation/:sessionId" element={<SimulationWorkspace />} />
        
        {/* Admin/Internal Pages - With Layout */}
        <Route element={<Layout><Dashboard /></Layout>} path="/dashboard" />
        <Route element={<Layout><AgentList /></Layout>} path="/admin/agents" />
        <Route element={<Layout><AgentChat /></Layout>} path="/chat/:agentId" />
        <Route element={<Layout><Orchestration /></Layout>} path="/orchestration" />
        
        {/* Catch-all route - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
