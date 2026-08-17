from rest_framework.permissions import BasePermission

from apps.users.models import User

from .rbac import has_permission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.SUPER_ADMIN)


class IsCompanyAdmin(BasePermission):
    """Admin of their own company, or platform Super Admin."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.Role.SUPER_ADMIN, User.Role.ADMIN)
        )


class IsSameCompany(BasePermission):
    """Object-level check: users may only touch objects belonging to their own company."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.SUPER_ADMIN:
            return True
        company_id = obj.id if obj.__class__.__name__ == 'Company' else obj.company_id
        return company_id == request.user.company_id


class RBACPermission(BasePermission):
    """Generic role-based permission: the view declares `permission_map`,
    a dict of {action: 'permission.code'}. Actions absent from the map are
    allowed to any authenticated user (e.g. read-only custom actions);
    be explicit in permission_map for anything that should be restricted.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        permission_map = getattr(view, 'permission_map', {})
        code = permission_map.get(view.action)
        if code is None:
            return True
        return has_permission(request.user, code)
