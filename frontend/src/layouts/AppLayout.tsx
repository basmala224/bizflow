import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/projects', label: 'Projects' },
  { to: '/tasks', label: 'Tasks' },
]

export function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-6">
        <span className="text-lg font-semibold text-gray-900">BizFlow</span>
        <div className="flex items-center gap-3 text-sm text-gray-600">
          <span>
            {user?.first_name} {user?.last_name} · {user?.role}
          </span>
          <button
            onClick={() => logout()}
            className="rounded-md border border-gray-300 px-2.5 py-1 text-xs text-gray-700 hover:bg-gray-100"
          >
            Sign out
          </button>
        </div>
      </header>
      <div className="flex">
        <nav className="w-56 shrink-0 border-r border-gray-200 bg-white p-4">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `block rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <main className="min-w-0 flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
