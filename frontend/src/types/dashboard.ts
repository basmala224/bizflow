export interface DashboardKpis {
  projects_total: number
  projects_active: number
  tasks_total: number
  tasks_completed: number
  employees_total: number
}

export interface ProjectsByStatus {
  status: string
  label: string
  count: number
}

export interface TasksCompletedByMonth {
  month: string
  count: number
}

export interface EmployeePerformance {
  user_id: number
  name: string
  completed_tasks: number
}

export interface DashboardData {
  kpis: DashboardKpis
  projects_by_status: ProjectsByStatus[]
  tasks_completed_by_month: TasksCompletedByMonth[]
  employee_performance: EmployeePerformance[]
}
