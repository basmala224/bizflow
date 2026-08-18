import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { taskService } from '../services/taskService'
import { TASK_STATUSES, TASK_STATUS_LABELS, type Comment, type Task } from '../types/task'
import { TaskFormModal } from './TaskFormModal'

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const taskId = Number(id)

  const [task, setTask] = useState<Task | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [showEditModal, setShowEditModal] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadAll = async () => {
    try {
      const [taskData, commentsData] = await Promise.all([
        taskService.get(taskId),
        taskService.listComments(taskId),
      ])
      setTask(taskData)
      setComments(commentsData)
    } catch {
      setError('Task not found.')
    }
  }

  useEffect(() => {
    loadAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId])

  const handleStatusChange = async (status: Task['status']) => {
    if (!task) return
    const updated = await taskService.setStatus(task.id, status)
    setTask(updated)
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim()) return
    await taskService.addComment(taskId, newComment.trim())
    setNewComment('')
    const commentsData = await taskService.listComments(taskId)
    setComments(commentsData)
  }

  const handleDeleteTask = async () => {
    if (!confirm('Delete this task? This cannot be undone.')) return
    await taskService.remove(taskId)
    navigate('/tasks')
  }

  if (error) {
    return (
      <AppLayout>
        <p className="text-sm text-red-600">{error}</p>
      </AppLayout>
    )
  }

  if (!task) {
    return (
      <AppLayout>
        <p className="text-sm text-gray-500">Loading...</p>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">{task.title}</h1>
          <p className="mt-1 text-sm text-gray-500">{task.description || 'No description.'}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowEditModal(true)} className="rounded-md border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50">
            Edit
          </button>
          <button onClick={handleDeleteTask} className="rounded-md border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50">
            Delete
          </button>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-4 gap-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Status</p>
          <select
            value={task.status}
            onChange={(e) => handleStatusChange(e.target.value as Task['status'])}
            className="mt-1 w-full rounded-md border border-gray-300 px-2 py-1 text-sm font-medium"
          >
            {TASK_STATUSES.map((s) => (
              <option key={s} value={s}>{TASK_STATUS_LABELS[s]}</option>
            ))}
          </select>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Priority</p>
          <p className="mt-1 font-medium">{task.priority}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Due date</p>
          <p className="mt-1 font-medium">{task.due_date ?? '—'}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Assignee</p>
          <p className="mt-1 font-medium">
            {task.assigned_to_detail ? `${task.assigned_to_detail.first_name} ${task.assigned_to_detail.last_name}` : 'Unassigned'}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-900">Comments</h2>
        <div className="mt-3 space-y-3">
          {comments.map((comment) => (
            <div key={comment.id} className="rounded-lg border border-gray-200 bg-white p-3">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span className="font-medium text-gray-700">
                  {comment.author_detail.first_name} {comment.author_detail.last_name}
                </span>
                <span>{new Date(comment.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-1 text-sm text-gray-700">{comment.content}</p>
            </div>
          ))}
          {comments.length === 0 && <p className="text-sm text-gray-500">No comments yet.</p>}
        </div>

        <form onSubmit={handleAddComment} className="mt-3 flex gap-2">
          <input
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
            className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm"
          />
          <button type="submit" disabled={!newComment.trim()} className="rounded-md bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
            Post
          </button>
        </form>
      </div>

      {showEditModal && (
        <TaskFormModal
          task={task}
          projectId={task.project}
          onClose={() => setShowEditModal(false)}
          onSaved={() => {
            setShowEditModal(false)
            loadAll()
          }}
        />
      )}
    </AppLayout>
  )
}
