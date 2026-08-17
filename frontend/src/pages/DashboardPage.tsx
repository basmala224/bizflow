import { AppLayout } from '../layouts/AppLayout'
import { useAuth } from '../hooks/useAuth'

export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <AppLayout>
      <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
      <p className="mt-2 text-gray-600">
        Welcome, {user?.first_name} {user?.last_name} — role: {user?.role}
      </p>
    </AppLayout>
  )
}
