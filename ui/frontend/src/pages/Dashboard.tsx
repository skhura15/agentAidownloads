export default function Dashboard() {
  return (
    <div className="animate-fade-in">
      <h2 className="text-3xl font-bold mb-6">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-xl font-semibold mb-2">Total Agents</h3>
          <p className="text-4xl font-bold text-primary-500">5</p>
        </div>
        <div className="card">
          <h3 className="text-xl font-semibold mb-2">Active Conversations</h3>
          <p className="text-4xl font-bold text-green-500">12</p>
        </div>
        <div className="card">
          <h3 className="text-xl font-semibold mb-2">Total Requests</h3>
          <p className="text-4xl font-bold text-blue-500">1,234</p>
        </div>
      </div>
    </div>
  )
}
