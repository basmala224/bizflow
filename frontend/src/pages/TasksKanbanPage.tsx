import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { projectService } from '../services/projectService'
import { taskService } from '../services/taskService'
import type { Project } from '../types/project'
import { TASK_STATUSES, TASK_STATUS_LABELS, type Task, type TaskStatus } from '../types/task'
import { TaskFormModal } from './TaskFormModal'

const priorityColors: Record<string, string> = {
  LOW: 'bg-gray-100 text-gray-700',
  MEDIUM: 'bg-blue-100 text-blue-700',
  HIGH: 'bg-amber-100 text-amber-700',
  CRITICAL: 'bg-red-100 text-red-700',
}

const columnColors: Record<TaskStatus, string> = {
  TODO: 'border-gray-300',
  IN_PROGRESS: 'border-blue-300',
  REVIEW: 'border-amber-300',
  DONE: 'border-green-300',
  BLOCKED: 'border-red-300',
}

export default function TasksKanbanPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [dragOverStatus, setDragOverStatus] = useState<TaskStatus | null>(null)

  useEffect(() => {
    projectService.list().then((data) => {
      setProjects(data.results)
      if (data.results.length > 0) setSelectedProjectId(data.results[0].id)
      else setIsLoading(false)
    })
  }, [])

  const loadTasks = async (projectId: number) => {
    setIsLoading(true)
    const data = await taskService.list({ project: projectId })
    setTasks(data.results)
    setIsLoading(false)
  }

  useEffect(() => {
    if (selectedProjectId) loadTasks(selectedProjectId)
  }, [selectedProjectId])

  const handleDrop = async (status: TaskStatus, taskId: number) => {
    setDragOverStatus(null)
    const task = tasks.find((t) => t.id === taskId)
    if (!task || task.status === status) return
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status } : t)))
    try {
      await taskService.setStatus(taskId, status)
    } catch {
      setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: task.status } : t)))
    }
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Tasks</h1>
        <div className="flex gap-2">
          <select
            value={selectedProjectId ?? ''}
            onChange={(e) => setSelectedProjectId(Number(e.target.value))}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button
            onClick={() => setShowCreateModal(true)}
            disabled={!selectedProjectId}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            New task
          </button>
        </div>
      </div>

      {projects.length === 0 && !isLoading ? (
        <p className="mt-6 text-sm text-gray-500">No projects yet — create a project first.</p>
      ) : (
        <div className="mt-6 grid grid-cols-5 gap-4">
          {TASK_STATUSES.map((columnStatus) => (
            <div
              key={columnStatus}
              onDragOver={(e) => {
                e.preventDefault()
                setDragOverStatus(columnStatus)
              }}
              onDragLeave={() => setDragOverStatus((s) => (s === columnStatus ? null : s))}
              onDrop={(e) => {
                e.preventDefault()
                const taskId = Number(e.dataTransfer.getData('text/plain'))
                handleDrop(columnStatus, taskId)
              }}
              className={`rounded-lg border-t-4 bg-gray-50 p-3 ${columnColors[columnStatus]} ${
                dragOverStatus === columnStatus ? 'ring-2 ring-indigo-300' : ''
              }`}
            >
              <h3 className="text-sm font-semibold text-gray-700">
                {TASK_STATUS_LABELS[columnStatus]}{' '}
                <span className="text-gray-400">({tasks.filter((t) => t.status === columnStatus).length})</span>
              </h3>
              <div className="mt-3 space-y-2">
                {tasks
                  .filter((t) => t.status === columnStatus)
                  .map((task) => (
                    <div
                      key={task.id}
                      draggable
                      onDragStart={(e) => e.dataTransfer.setData('text/plain', String(task.id))}
                      className="cursor-move rounded-md border border-gray-200 bg-white p-3 shadow-sm hover:shadow"
                    >
                      <Link to={`/tasks/${task.id}`} className="text-sm font-medium text-gray-900 hover:text-indigo-600">
                        {task.title}
                      </Link>
                      <div className="mt-2 flex items-center justify-between">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${priorityColors[task.priority]}`}>
                          {task.priority}
                        </span>
                        {task.assigned_to_detail && (
                          <span className="text-xs text-gray-500">
                            {task.assigned_to_detail.first_name} {task.assigned_to_detail.last_name}
                          </span>
                        )}
                      </div>
                      {task.due_date && <p className="mt-1 text-xs text-gray-400">Due {task.due_date}</p>}
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && selectedProjectId && (
        <TaskFormModal
          projectId={selectedProjectId}
          onClose={() => setShowCreateModal(false)}
          onSaved={() => {
            setShowCreateModal(false)
            loadTasks(selectedProjectId)
          }}
        />
      )}
    </AppLayout>
  )
}
