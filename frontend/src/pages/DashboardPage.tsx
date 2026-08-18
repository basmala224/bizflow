import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Label,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { AppLayout } from '../layouts/AppLayout'
import { useAuth } from '../hooks/useAuth'
import { dashboardService } from '../services/dashboardService'
import type { DashboardData } from '../types/dashboard'

// Fixed categorical order mapped to Project.Status — never reassigned by filter/rank.
const STATUS_COLORS: Record<string, string> = {
  PLANNED: '#2a78d6',
  IN_PROGRESS: '#eb6834',
  ON_HOLD: '#1baf7a',
  COMPLETED: '#eda100',
  CANCELLED: '#e87ba4',
}
const SERIES_BLUE = '#2a78d6'

const INK_PRIMARY = '#0b0b0b'
const INK_MUTED = '#898781'
const GRIDLINE = '#e1e0d9'

function KpiTile({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [data, setData] = useState<DashboardData | null>(null)

  useEffect(() => {
    dashboardService.get().then(setData)
  }, [])

  return (
    <AppLayout>
      <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
      <p className="mt-1 text-sm text-gray-500">
        Welcome, {user?.first_name} {user?.last_name} · {user?.role}
      </p>

      {!data ? (
        <p className="mt-6 text-sm text-gray-500">Loading...</p>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-5 gap-4">
            <KpiTile label="Projects" value={data.kpis.projects_total} />
            <KpiTile label="Active projects" value={data.kpis.projects_active} />
            <KpiTile label="Tasks" value={data.kpis.tasks_total} />
            <KpiTile label="Completed tasks" value={data.kpis.tasks_completed} />
            <KpiTile label="Employees" value={data.kpis.employees_total} />
          </div>

          <div className="mt-8 grid grid-cols-2 gap-6">
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <h2 className="text-sm font-semibold text-gray-900">Projects by status</h2>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.projects_by_status} margin={{ top: 16, right: 8, left: 0, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={GRIDLINE} />
                    <XAxis dataKey="label" tick={{ fill: INK_MUTED, fontSize: 12 }} axisLine={{ stroke: GRIDLINE }} tickLine={false} />
                    <YAxis allowDecimals={false} tick={{ fill: INK_MUTED, fontSize: 12 }} axisLine={false} tickLine={false} width={28} />
                    <Tooltip cursor={{ fill: '#f9f9f7' }} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={48}>
                      {data.projects_by_status.map((entry) => (
                        <Cell key={entry.status} fill={STATUS_COLORS[entry.status] ?? SERIES_BLUE} />
                      ))}
                      <LabelList dataKey="count" position="top" fill={INK_PRIMARY} fontSize={12} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <h2 className="text-sm font-semibold text-gray-900">Tasks completed per month</h2>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.tasks_completed_by_month} margin={{ top: 16, right: 8, left: 0, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke={GRIDLINE} />
                    <XAxis dataKey="month" tick={{ fill: INK_MUTED, fontSize: 12 }} axisLine={{ stroke: GRIDLINE }} tickLine={false} />
                    <YAxis allowDecimals={false} tick={{ fill: INK_MUTED, fontSize: 12 }} axisLine={false} tickLine={false} width={28}>
                      <Label value="Completed tasks" angle={-90} position="insideLeft" style={{ fill: INK_MUTED, fontSize: 11 }} />
                    </YAxis>
                    <Tooltip cursor={{ stroke: GRIDLINE }} />
                    <Line type="monotone" dataKey="count" stroke={SERIES_BLUE} strokeWidth={2} dot={{ r: 4, fill: SERIES_BLUE }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-lg border border-gray-200 bg-white p-4">
            <h2 className="text-sm font-semibold text-gray-900">Top performers (completed tasks)</h2>
            {data.employee_performance.length === 0 ? (
              <p className="mt-4 text-sm text-gray-500">No completed tasks yet.</p>
            ) : (
              <div className="mt-4 h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data.employee_performance}
                    layout="vertical"
                    margin={{ top: 0, right: 24, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid horizontal={false} stroke={GRIDLINE} />
                    <XAxis type="number" allowDecimals={false} tick={{ fill: INK_MUTED, fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis
                      type="category"
                      dataKey="name"
                      tick={{ fill: INK_MUTED, fontSize: 12 }}
                      axisLine={{ stroke: GRIDLINE }}
                      tickLine={false}
                      width={120}
                    />
                    <Tooltip cursor={{ fill: '#f9f9f7' }} />
                    <Bar dataKey="completed_tasks" fill={SERIES_BLUE} radius={[0, 4, 4, 0]} maxBarSize={24}>
                      <LabelList dataKey="completed_tasks" position="right" fill={INK_PRIMARY} fontSize={12} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </>
      )}
    </AppLayout>
  )
}
