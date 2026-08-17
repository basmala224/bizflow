import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { projectService } from '../services/projectService'
import { userService } from '../services/userService'
import type { User } from '../types/auth'
import { PROJECT_PRIORITIES, PROJECT_STATUSES, type Project } from '../types/project'

const schema = z.object({
  name: z.string().min(2, 'Name is required'),
  description: z.string().optional(),
  status: z.string(),
  priority: z.string(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  manager: z.string().optional(),
})

type ProjectForm = z.infer<typeof schema>

export function ProjectFormModal({
  project,
  onClose,
  onSaved,
}: {
  project?: Project
  onClose: () => void
  onSaved: () => void
}) {
  const [users, setUsers] = useState<User[]>([])
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProjectForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: project?.name ?? '',
      description: project?.description ?? '',
      status: project?.status ?? 'PLANNED',
      priority: project?.priority ?? 'MEDIUM',
      start_date: project?.start_date ?? '',
      end_date: project?.end_date ?? '',
      manager: project?.manager ? String(project.manager) : '',
    },
  })

  useEffect(() => {
    userService.list().then((data) => setUsers(data.results))
  }, [])

  const onSubmit = async (data: ProjectForm) => {
    setServerError(null)
    const payload = {
      ...data,
      start_date: data.start_date || null,
      end_date: data.end_date || null,
      manager: data.manager ? Number(data.manager) : null,
    }
    try {
      if (project) {
        await projectService.update(project.id, payload)
      } else {
        await projectService.create(payload)
      }
      onSaved()
    } catch {
      setServerError('Could not save the project. Please check the fields.')
    }
  }

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 px-4">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-lg">
        <h2 className="text-lg font-semibold text-gray-900">{project ? 'Edit project' : 'New project'}</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input {...register('name')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea {...register('description')} rows={2} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Status</label>
              <select {...register('status')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
                {PROJECT_STATUSES.map((s) => (
                  <option key={s} value={s}>{s.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Priority</label>
              <select {...register('priority')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
                {PROJECT_PRIORITIES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Start date</label>
              <input type="date" {...register('start_date')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">End date</label>
              <input type="date" {...register('end_date')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Manager</label>
            <select {...register('manager')} className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
              <option value="">Unassigned</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
              ))}
            </select>
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
