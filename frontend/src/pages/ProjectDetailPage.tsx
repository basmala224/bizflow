import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import { projectService } from '../services/projectService'
import { userService } from '../services/userService'
import type { User } from '../types/auth'
import { PROJECT_MEMBER_ROLES, type Project, type ProjectMember, type ProjectMemberRole } from '../types/project'
import { ProjectFormModal } from './ProjectFormModal'

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const projectId = Number(id)

  const [project, setProject] = useState<Project | null>(null)
  const [members, setMembers] = useState<ProjectMember[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [newMemberId, setNewMemberId] = useState('')
  const [newMemberRole, setNewMemberRole] = useState<ProjectMemberRole>('DEVELOPER')
  const [showEditModal, setShowEditModal] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadAll = async () => {
    try {
      const [projectData, membersData, usersData] = await Promise.all([
        projectService.get(projectId),
        projectService.listMembers(projectId),
        userService.list(),
      ])
      setProject(projectData)
      setMembers(membersData)
      setUsers(usersData.results)
    } catch {
      setError('Project not found.')
    }
  }

  useEffect(() => {
    loadAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId])

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMemberId) return
    await projectService.addMember(projectId, Number(newMemberId), newMemberRole)
    setNewMemberId('')
    loadAll()
  }

  const handleRemoveMember = async (userId: number) => {
    await projectService.removeMember(projectId, userId)
    loadAll()
  }

  const handleDeleteProject = async () => {
    if (!confirm('Delete this project? This cannot be undone.')) return
    await projectService.remove(projectId)
    navigate('/projects')
  }

  if (error) {
    return (
      <AppLayout>
        <p className="text-sm text-red-600">{error}</p>
      </AppLayout>
    )
  }

  if (!project) {
    return (
      <AppLayout>
        <p className="text-sm text-gray-500">Loading...</p>
      </AppLayout>
    )
  }

  const memberIds = new Set(members.map((m) => m.user))
  const availableUsers = users.filter((u) => !memberIds.has(u.id))

  return (
    <AppLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">{project.name}</h1>
          <p className="mt-1 text-sm text-gray-500">{project.description || 'No description.'}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowEditModal(true)} className="rounded-md border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50">
            Edit
          </button>
          <button onClick={handleDeleteProject} className="rounded-md border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50">
            Delete
          </button>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-4 gap-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Status</p>
          <p className="mt-1 font-medium">{project.status.replace('_', ' ')}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Priority</p>
          <p className="mt-1 font-medium">{project.priority}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Progress</p>
          <p className="mt-1 font-medium">{project.progress}%</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500">Manager</p>
          <p className="mt-1 font-medium">
            {project.manager_detail ? `${project.manager_detail.first_name} ${project.manager_detail.last_name}` : 'Unassigned'}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-900">Members</h2>
        <div className="mt-3 overflow-hidden rounded-lg border border-gray-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-gray-200 bg-gray-50 text-gray-500">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Email</th>
                <th className="px-4 py-2 font-medium">Role</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {members.map((member) => (
                <tr key={member.id}>
                  <td className="px-4 py-2">{member.user_detail.first_name} {member.user_detail.last_name}</td>
                  <td className="px-4 py-2 text-gray-500">{member.user_detail.email}</td>
                  <td className="px-4 py-2 text-gray-500">{member.role}</td>
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => handleRemoveMember(member.user)} className="text-xs text-red-600 hover:underline">
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
              {members.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-3 text-sm text-gray-500">No members yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <form onSubmit={handleAddMember} className="mt-3 flex gap-2">
          <select value={newMemberId} onChange={(e) => setNewMemberId(e.target.value)} className="rounded-md border border-gray-300 px-3 py-1.5 text-sm">
            <option value="">Select a user...</option>
            {availableUsers.map((u) => (
              <option key={u.id} value={u.id}>{u.first_name} {u.last_name} ({u.email})</option>
            ))}
          </select>
          <select value={newMemberRole} onChange={(e) => setNewMemberRole(e.target.value as ProjectMemberRole)} className="rounded-md border border-gray-300 px-3 py-1.5 text-sm">
            {PROJECT_MEMBER_ROLES.map((role) => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
          <button type="submit" disabled={!newMemberId} className="rounded-md bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
            Add member
          </button>
        </form>
      </div>

      {showEditModal && (
        <ProjectFormModal
          project={project}
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
