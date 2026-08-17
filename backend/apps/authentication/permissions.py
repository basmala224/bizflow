from rest_framework.permissions import BasePermission

from apps.users.models import User


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
        obj_company = getattr(obj, 'company', obj if obj.__class__.__name__ == 'Company' else None)
        return obj_company is not None and obj_company == request.user.company
