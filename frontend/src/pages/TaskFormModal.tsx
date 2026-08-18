import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { taskService } from '../services/taskService'
import { userService } from '../services/userService'
import type { User } from '../types/auth'
import { TASK_PRIORITIES, type Task } from '../types/task'

const schema = z.object({
  title: z.string().min(2, 'Title is required'),
  description: z.string().optional(),
  priority: z.string(),
  assigned_to: z.string().optional(),
  due_date: z.string().optional(),
  estimated_hours: z.string().optional(),
  actual_hours: z.string().optional(),
})

type TaskForm = z.infer<typeof schema>

export function TaskFormModal({
  task,
  projectId,
  onClose,
  onSaved,
}: {
  task?: Task
  projectId: number
  onClose: () => void
  onSaved: () => void
}) {
  const [users, setUsers] = useState<User[]>([])
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TaskForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: task?.title ?? '',
      description: task?.description ?? '',
      priority: task?.priority ?? 'MEDIUM',
      assigned_to: task?.assigned_to ? String(task.assigned_to) : '',
      due_date: task?.due_date ?? '',
      estimated_hours: task?.estimated_hours ?? '',
      actual_hours: task?.actual_hours ?? '',
    },
  })

  useEffect(() => {
    userService.list().then((data) => setUsers(data.results))
  }, [])

  const onSubmit = async (data: TaskForm) => {
    setServerError(null)
    const payload = {
      ...data,
      project: projectId,
      assigned_to: data.assigned_to ? Number(data.assigned_to) : null,
      due_date: data.due_date || null,
      estimated_hours: data.estimated_hours || null,
      actual_hours: data.actual_hours || null,
    }
    try {
      if (task) {
        await taskService.update(task.id, payload)
      } else {
        await taskService.create(payload)
      }
      onSaved()
    } catch {
      setServerError('Could not save the task. Please check the fields (assignee must be a project member).')
    }
  }

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 px-4">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-lg">
        <h2 className="text-lg font-semibold text-gray-900">{task ? 'Edit task' : 'New task'}</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Title</label>
            <input {...register('title')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea {...register('description')} rows={2} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Priority</label>
              <select {...register('priority')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
                {TASK_PRIORITIES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Due date</label>
              <input type="date" {...register('due_date')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Assignee</label>
            <select {...register('assigned_to')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
              <option value="">Unassigned</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Estimated hours</label>
              <input type="number" step="0.5" {...register('estimated_hours')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Actual hours</label>
              <input type="number" step="0.5" {...register('actual_hours')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>
          {serverError && <p className="text-sm text-red-600">{serverError}</p>}
          <div className="mt-4 flex justify-end gap-2">
            <button type="button" onClick={onClose} className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
