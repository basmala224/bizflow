"""Static RBAC permission matrix — see cahier des charges §10.

Four roles (SUPER_ADMIN, ADMIN, MANAGER, EMPLOYEE), each mapped to a set of
fine-grained permission codes. Kept as plain Python (not DB-backed models)
since the role set is fixed and small; this avoids an unnecessary
Role/Permission table + M2M for a project with only four roles.
"""

from apps.users.models import User

PERMISSIONS = {
    'companies.manage',
    'users.view', 'users.create', 'users.update', 'users.delete',
    'projects.view', 'projects.create', 'projects.update', 'projects.delete',
    'tasks.view', 'tasks.create', 'tasks.update', 'tasks.delete',
    'comments.view', 'comments.create',
    'reports.view',
    'audit.view',
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    User.Role.SUPER_ADMIN: set(PERMISSIONS),
    User.Role.ADMIN: {
        'users.view', 'users.create', 'users.update', 'users.delete',
        'projects.view', 'projects.create', 'projects.update', 'projects.delete',
        'tasks.view', 'tasks.create', 'tasks.update', 'tasks.delete',
        'comments.view', 'comments.create',
        'reports.view', 'audit.view',
    },
    User.Role.MANAGER: {
        'users.view',
        'projects.view',
        'tasks.view', 'tasks.create', 'tasks.update',
        'comments.view', 'comments.create',
        'reports.view',
    },
    User.Role.EMPLOYEE: {
        'projects.view',
        'tasks.view', 'tasks.update',
        'comments.view', 'comments.create',
    },
}


def has_permission(user, code: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    return code in ROLE_PERMISSIONS.get(user.role, set())
